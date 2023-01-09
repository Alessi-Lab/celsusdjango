import io
import json

import pandas as pd
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny,IsAdminUser
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.response import Response
from rest_framework import status
from django_sendfile import sendfile
from uniprotparser.betaparser import UniprotParser
import requests as req
from celsus.models import Project, GeneNameMap, UniprotRecord, SocialPlatform, ExtraProperties
from celsusdjango import settings
from celsus.google_views import GoogleOAuth2AdapterIdToken # import custom adapter
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
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


class UserView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if 'HTTP_AUTHORIZATION' in request.META:
            authorization = request.META['HTTP_AUTHORIZATION'].replace("Bearer ", "")
            access_token = AccessToken(authorization)
            user = User.objects.filter(pk=access_token["user_id"]).first()
            user_json = {
                    "username": user.username,
                    "id": user.id,
                    "total_curtain": user.curtain.count()
                }



            if user.is_staff:
                user_json["is_staff"] = True
            if settings.CURTAIN_ALLOW_NON_STAFF_DELETE:
                user_json["can_delete"] = True
            else:
                user_json["can_delete"] = user_json["is_staff"]

            user_json["curtain_link_limit"] = user.extraproperties.curtain_link_limits
            user_json["curtain_link_limit_exceed"] = user.extraproperties.curtain_link_limit_exceed
            if user:
                return Response(user_json)
        return Response(status=status.HTTP_404_NOT_FOUND)

class GetOverview(APIView):
    permission_classes = (AllowAny,)

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


class UniprotRefreshView(APIView):
    permission_classes = (IsAdminUser, )

    def post(self, request):
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
                    accession_map[acc]["object"].primary_uniprot_record = uniprot_record_map[accession_map[acc]["primary_id"]]
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
        return Response(status=status.HTTP_204_NO_CONTENT)

class NetPhosView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        da = req.post(settings.NETPHOS_WEB_URL, json={"id": self.request.data["id"], "fasta": self.request.data["fasta"]})
        return Response(da.json())


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2AdapterIdToken
    client_class = OAuth2Client
    parser_classes = [JSONParser,]


class GoogleLogin2(APIView): # if you want to use Implicit Grant, use this
    permission_classes = (AllowAny,)
    def post(self, request):
        print(self.request.data)
        try:
            idinfo = id_token.verify_oauth2_token(self.request.data["auth_token"], requests.Request(), settings.SOCIALACCOUNT_PROVIDERS.get("google").get("APP").get("client_id"))
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user = User.objects.filter(email=idinfo["email"]).first()
        if user:
            refresh_token = RefreshToken.for_user(user)
            user.is_authenticated = True
            return Response(data={"refresh": str(refresh_token), "access": str(refresh_token.access_token)})
        else:
            user = User.objects.create_user(username=idinfo["email"], password=User.objects.make_random_password(), email=idinfo["email"])
            user.is_authenticated = True
            user.save()
            ex = ExtraProperties(user=user)
            social = SocialPlatform.objects.get_or_create(SocialPlatform(name="Google"))
            social.save()
            ex.social_platform = social
            ex.save()
            refresh_token = RefreshToken.for_user(user)
            return Response(data={"refresh": str(refresh_token), "access": str(refresh_token.access_token)})

class ORCIDOAUTHView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        print(self.request.data)
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
            response = req.post("https://orcid.org/oauth/token", payload, headers=headers)
            data = json.loads(response.content.decode())
            try:
                user = User.objects.filter(username=data["orcid"]).first()
                print(user)
                if user:
                    refresh_token = RefreshToken.for_user(user)
                    #user.is_authenticated = True
                    #user.save()
                    return Response(data={"refresh": str(refresh_token), "access": str(refresh_token.access_token)})
                else:
                    user = User.objects.create_user(username=data["orcid"],
                                                    password=User.objects.make_random_password())

                    #user.is_authenticated = True

                    #user.save()
                    ex = ExtraProperties(user=user)
                    ex.save()
                    ex = ExtraProperties(user=user)
                    social = SocialPlatform.objects.get_or_create(SocialPlatform(name="ORCID"))
                    social.save()
                    ex.social_platform = social
                    ex.save()
                    refresh_token = RefreshToken.for_user(user)
                    return Response(data={"refresh": str(refresh_token), "access": str(refresh_token.access_token)})
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class SitePropertiesView(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, format=None):
        return Response(data={
            "non_user_post": settings.CURTAIN_ALLOW_NON_USER_POST
        })