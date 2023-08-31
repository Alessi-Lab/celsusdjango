import io
import json

import pandas as pd
from request.models import Request as django_request
#from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
#from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

#from google.auth.transport import requests
#from google.oauth2 import id_token
#from rest_framework.generics import GenericAPIView
#from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny,IsAdminUser
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.response import Response
from rest_framework import status
from uniprotparser.betaparser import UniprotParser
import requests as req
from celsus.models import Curtain, Project, GeneNameMap, UniprotRecord, SocialPlatform, ExtraProperties, DataFilterList
#from celsus.serializers import DataFilterListSerializer
from celsusdjango import settings
#from celsus.google_views import GoogleOAuth2AdapterIdToken # import custom adapter
#from dj_rest_auth.registration.views import SocialLoginView
#from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from statsmodels.stats.weightstats import ttest_ind

# Logout view used to blacklist refresh token
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    # only access this view if user is authenticated

    def post(self, request):
        # try to blacklist the refresh token and return 205 if successful or 400 if not successful (bad request)
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CSRFTokenView(APIView):
    permission_classes = (AllowAny,)

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_204_NO_CONTENT)

# View to get user information
class UserView(APIView):
    permission_classes = (IsAuthenticated,)
    # only access this view if user is authenticated

    def post(self, request, *args, **kwargs):
        # get user information and return it as json
        # if user is staff, return is_staff = true
        if 'HTTP_AUTHORIZATION' in request.META:
            authorization = request.META['HTTP_AUTHORIZATION'].replace("Bearer ", "")
            # get user from access token
            access_token = AccessToken(authorization)
            user = User.objects.filter(pk=access_token["user_id"]).first()
            extra = ExtraProperties.objects.filter(user=user).first()
            # create extra properties if they don't exist
            if not extra:
                extra = ExtraProperties(user=user)
                extra.save()
            # create user json
            user_json = {
                    "username": user.username,
                    "id": user.id,
                    "total_curtain": user.curtain.count()
                }
            if user.is_staff:
                user_json["is_staff"] = True
            else:
                user_json["is_staff"] = False
            if settings.CURTAIN_ALLOW_NON_STAFF_DELETE:
                user_json["can_delete"] = True
            else:
                user_json["can_delete"] = user_json["is_staff"]
            user_json["curtain_link_limit"] = user.extraproperties.curtain_link_limits
            user_json["curtain_link_limit_exceed"] = user.extraproperties.curtain_link_limit_exceed
            # return user json
            if user:
                return Response(user_json)
        # if user is not authenticated, return 404
        return Response(status=status.HTTP_404_NOT_FOUND)

# Get database project overview (total projects, total unique proteins, average unique proteins per project)
class GetOverview(APIView):
    permission_classes = (AllowAny,)
    # user can access without being authenticated

    def get(self, request):
        queryset = Project.objects.all()
        total = queryset.count()
        queryset_ptm = queryset.filter(ptm_data=1)
        total_queryset_ptm = queryset_ptm.count()
        unique_proteins_set = set()
        for i in GeneNameMap.objects.all():
            unique_proteins_set.add(i.gene_names)

        ptm_unique_proteins = []
        total_proteomics_unique_proteins = []

        for i in queryset:
            if i.ptm_data:
                ptm_unique_proteins.append(len(i.get_unique_proteins()))
            else:
                total_proteomics_unique_proteins.append(len(i.get_unique_proteins()))

        return Response(
            {
                "project_count": {
                    "total": total,
                    "total_proteomics": total-total_queryset_ptm,
                    "ptm_proteomics": total_queryset_ptm
                },
                "unique_proteins": {
                    "unique_proteins": len(unique_proteins_set),
                    "average_unique_proteins": {
                        "total_proteomics": sum(total_proteomics_unique_proteins)/len(total_proteomics_unique_proteins),
                        "ptm_proteomics": sum(ptm_unique_proteins)/len(ptm_unique_proteins)
                    }
                }
            }
        )


def refresh_uniprot():
    accession_id = set()
    accession_map = {}
    for i in GeneNameMap.objects.all():
        acc_split = i.accession_id.split(";")
        accession_map[i.accession_id] = {"entries": acc_split, "primary_id": acc_split[0].split("-")[0], "object": i}
        for i2 in acc_split:
            # acc_comp = i2.split("-")
            #
            # if acc_comp[0] not in accession_map:
            #     accession_map[acc_comp[0]] = {"primary_acc": acc_comp[0], "acc_map": {}}
            # if len(acc_comp) > 1:
            #     if i.accession_id not in accession_map[acc_comp[0]]["acc_map"]:
            #         accession_map[acc_comp[0]]["acc_map"][i.accession_id] = {}
            #     if i2 not in accession_map[acc_comp[0]]["acc_map"][i.accession_id]:
            #         accession_map[acc_comp[0]]["acc_map"][i.accession_id][i2] = i

            accession_id.add(i2)
    accession_id = list(accession_id)
    parser = UniprotParser(include_isoform=True)
    uni_df = []
    for p in parser.parse(accession_id):
        uniprot_df = pd.read_csv(io.StringIO(p), sep="\t")
        uni_df.append(uniprot_df)
    if len(uni_df) == 1:
        uni_df = uni_df[0]
    else:
        uni_df = pd.concat(uni_df, ignore_index=True)
    uniprot_record_map = {}
    with transaction.atomic():
        for ind, row in uni_df.iterrows():
            uniprot_record = UniprotRecord.objects.filter(entry=row["Entry"]).first()
            if uniprot_record:
                uniprot_record.record = json.dumps(row.to_dict())
            else:
                uniprot_record = UniprotRecord(entry=row["Entry"], record=json.dumps(row.to_dict()))
            uniprot_record.save()
            uniprot_record_map[uniprot_record.entry] = uniprot_record
        for acc in accession_map:
            accession_map[acc]["object"].clean()
            for i in accession_map[acc]["entries"]:
                if i in uniprot_record_map:
                    accession_map[acc]["object"].uniprot_record.add(uniprot_record_map[i])
            if accession_map[acc]["primary_id"] in uniprot_record_map:
                accession_map[acc]["object"].primary_uniprot_record = uniprot_record_map[
                    accession_map[acc]["primary_id"]]
            accession_map[acc]["object"].entry = accession_map[acc]["primary_id"]
            accession_map[acc]["object"].save()

        # for ind, row in uni_df.iterrows():
        #     if row["From"] in accession_map:
        #         accession_map[row["From"]].entry = row["Entry"]
        #         if row["Entry"] in uniprot_record_map:
        #             accession_map[row["From"]].uniprot_record = uniprot_record_map[row["Entry"]]
        #         if pd.notnull(row["Gene Names"]):
        #             accession_map[row["From"]].gene_names = row["Gene Names"].upper()
        #         else:
        #             accession_map[row["From"]].gene_names = row["Entry"]
        #         accession_map[row["From"]].save()

class UniprotRefreshView(APIView):
    permission_classes = (IsAdminUser, )

    def post(self, request):
        refresh_uniprot()
        return Response(status=status.HTTP_204_NO_CONTENT)

class NetPhosView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        da = req.post(settings.NETPHOS_WEB_URL, json={"id": self.request.data["id"], "fasta": self.request.data["fasta"]})
        return Response(da.json())


# class GoogleLogin(SocialLoginView):
#     adapter_class = GoogleOAuth2AdapterIdToken
#     client_class = OAuth2Client
#     parser_classes = [JSONParser,]


# class GoogleLogin2(APIView): # if you want to use Implicit Grant, use this
#     permission_classes = (AllowAny,)
#     def post(self, request):
#         print(self.request.data)
#         try:
#             idinfo = id_token.verify_oauth2_token(self.request.data["auth_token"], requests.Request(), settings.SOCIALACCOUNT_PROVIDERS.get("google").get("APP").get("client_id"))
#         except:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#         user = User.objects.filter(email=idinfo["email"]).first()
#         if user:
#             refresh_token = RefreshToken.for_user(user)
#             user.is_authenticated = True
#             return Response(data={"refresh": str(refresh_token), "access": str(refresh_token.access_token)})
#         else:
#             user = User.objects.create_user(username=idinfo["email"], password=User.objects.make_random_password(), email=idinfo["email"])
#             user.is_authenticated = True
#             user.save()
#             ex = ExtraProperties(user=user)
#             social = SocialPlatform.objects.get_or_create(SocialPlatform(name="Google"))
#             social.save()
#             ex.social_platform = social
#             ex.save()
#             refresh_token = RefreshToken.for_user(user)
#             return Response(data={"refresh": str(refresh_token), "access": str(refresh_token.access_token)})

# View for handling ORCID OAuth
class ORCIDOAUTHView(APIView):
    permission_classes = (AllowAny,)
    # user can post to this view without being authenticated
    # this view will handle the OAuth process

    def post(self, request):
        print(self.request.data)
        # check if the request contains the auth_token and redirect_uri
        if "auth_token" in self.request.data and "redirect_uri" in self.request.data:
            payload = {
                "client_id": settings.ORCID["client_id"],
                "client_secret": settings.ORCID["secret"],
                "grant_type": "authorization_code",
                "code": self.request.data["auth_token"],
                "redirect_uri": self.request.data["redirect_uri"]
            }
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            # post the request to the ORCID API to get the user data
            response = req.post("https://orcid.org/oauth/token", payload, headers=headers)
            data = json.loads(response.content.decode())
            # check if the user has already been created from the ORCID ID
            try:
                # get the user from the ORCID ID
                user = User.objects.filter(username=data["orcid"]).first()

                print(user)
                # check if the user exists
                if user:
                    # check if the user has been assigned a social platform
                    social = SocialPlatform.objects.filter(name="ORCID").first()
                    if social:
                        if social is not user.extraproperties.social_platform:
                            # assign the user to the social platform
                            user.extraproperties.social_platform = social
                            user.extraproperties.save()
                    # create a refresh token for the user
                    refresh_token = RefreshToken.for_user(user)
                    #user.is_authenticated = True
                    #user.save()
                    return Response(data={"refresh": str(refresh_token), "access": str(refresh_token.access_token)})
                else:
                    # create a new user with the ORCID ID as the username
                    user = User.objects.create_user(username=data["orcid"],
                                                    password=User.objects.make_random_password())
                    #user.is_authenticated = True

                    #user.save()
                    # create a new ExtraProperties object for the user
                    ex = ExtraProperties(user=user)
                    ex.save()
                    # assign the user to the ORCID social platform
                    social = SocialPlatform.objects.get_or_create(SocialPlatform(name="ORCID"))
                    social.save()
                    ex.social_platform = social
                    ex.save()
                    # create a refresh token for the user
                    refresh_token = RefreshToken.for_user(user)
                    return Response(data={"refresh": str(refresh_token), "access": str(refresh_token.access_token)})
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)

# Get general site properties
class SitePropertiesView(APIView):
    permission_classes = (AllowAny,)
    # user can get this view without being authenticated

    def get(self, request, format=None):
        return Response(data={
            "non_user_post": settings.CURTAIN_ALLOW_NON_USER_POST
        })

# Kinase Library Proxy view for getting kinase scores
class KinaseLibraryProxyView(APIView):
    permission_classes = (AllowAny,)
    # user can get this view without being authenticated

    def get(self, request, format=None):
        # check if the request contains the sequence
        if request.query_params['sequence']:
            res = req.get(f"https://kinase-library.phosphosite.org/api/scorer/score-site/{request.query_params['sequence']}/")
            return Response(data=res.json())
        # if the request does not contain the sequence, return a 400 error
        return Response(status=status.HTTP_400_BAD_REQUEST)

# View for handling the checking of job status
# class CheckJobView(APIView):
#     permission_classes = (AllowAny,)
#
#     def get(self, request, format=None):
#         if request.query_params['id']:
#             task = fetch(request.query_params['id'])
#             if task:
#                 resp = {"job_id": request.query_params['id'], "status": "progressing"}
#                 if task.success:
#                     resp["status"] = "completed"
#
#                     return Response(data=resp)
#                 elif task.stopped:
#                     return Response(data=resp)
#                 else:
#                     return Response(data=resp)
#             else:
#                 return Response(status=status.HTTP_404_NOT_FOUND)
#         return Response(status=status.HTTP_400_BAD_REQUEST)


# View for getting Curtain download stats
class DownloadStatsView(APIView):
    permission_classes = (AllowAny,)
    # user can get this view without being authenticated

    def get(self, request, format=None):
        # get the number of downloads
        # this is done by filtering the django_request table for requests that match the download url
        download_stats = django_request.objects.filter(path__regex="\/curtain\/[a-z0-9\-]+\/download\/\w*").count()
        return Response(data={
            "download": download_stats
        })

class InteractomeAtlasProxyView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        if request.data["link"]:
            res = req.get(request.data["link"].replace("https", "http"))
            return Response(data=res.json())
        return Response(status=status.HTTP_400_BAD_REQUEST)


class PrimitiveStatsTestView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        test_type = request.data["type"]
        test_data = request.data["data"]
        if test_type == "t-test":
            st, p, f = ttest_ind(test_data[0], test_data[1])
            return Response(data={
                "test_statistic": st, "p_value": p, "degrees_of_freedom": f
            })
        print(test_type, test_data)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CompareSessionView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        id_list = request.data["idList"]
        curtain_list = Curtain.objects.filter(link_id__in=id_list)
        to_be_processed_list = []
        for item in curtain_list:
            owners = item.owners.all()
            if len(owners) > 0:
                if not item.enable:
                    if request.user and request.user.is_authenticated and request.user in owners and request.user:
                        to_be_processed_list.append(item)
                else:
                    to_be_processed_list.append(item)
            else:
                to_be_processed_list.append(item)
        print(to_be_processed_list)
        study_list = request.data["studyList"]
        result = {}
        for i in to_be_processed_list:
            data = req.get(i.file.url).json()
            differential_form = data["differentialForm"]

            pid_col = differential_form["_primaryIDs"]
            fc_col = differential_form["_foldChange"]
            significant_col = differential_form["_significant"]
            string_data = io.StringIO(data["processed"])
            df = pd.read_csv(string_data, sep="\t")
            if len(differential_form["_comparisonSelect"]) > 0:
                if differential_form["_comparison"] in df.columns:
                    df[differential_form["_comparison"]] = df[differential_form["_comparison"]].astype(str)
                    if type(differential_form["_comparisonSelect"]) == str:
                        df = df[df[differential_form["_comparison"]] == differential_form["_comparisonSelect"]]
                    else:
                        df = df[differential_form["_comparison"].isin(differential_form["_comparisonSelect"])]
            print(differential_form["_transformFC"])
            if differential_form["_transformFC"]:
                df[fc_col].apply(lambda x: np.log2(x) if x >= 0 else -np.log2(-x))
            print(differential_form["_transformSignificant"])
            if differential_form["_transformSignificant"]:
                df[significant_col] = -np.log10(df[significant_col])
            if request.data["matchType"] == "primaryID":
                df = df[df[pid_col].isin(study_list)]
                df = df[[pid_col, fc_col, significant_col]]
                result[i.link_id] = df.to_dict(orient="records")
        print(result)
        if result:
            return Response(data=result)
        return Response(data={})

