"""celsusdjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.template.defaulttags import url
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf.urls.static import static

from celsus.models import File
from celsus.view_sets import UserViewSet, ProjectViewSet, AuthorViewSet, FileViewSet, OrganismViewSet, \
    OrganismPartViewSet, CellTypeViewSet, TissueTypeViewSet, ExperimentTypeViewSet, QuantificationMethodViewSet, \
    KeywordViewSet, RawSampleColumnViewSet, DifferentialSampleColumnViewSet, RawDataViewSet, \
    DifferentialAnalysisDataViewSet, InstrumentViewSet, DiseaseViewSet, CurtainViewSet, ComparisonViewSet, \
    GeneNameMapViewSet, LabGroupViewSet, UniprotRecordViewSet
from django.conf import settings

from celsus.views import LogoutView, CSRFTokenView, GetOverview, UniprotRefreshView, UserView, NetPhosView, GoogleLogin, \
    GoogleLogin2, ORCIDOAUTHView, SitePropertiesView

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'authors', AuthorViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'files', FileViewSet)
router.register(r'keywords', KeywordViewSet)
router.register(r'organisms', OrganismViewSet)
router.register(r'organism_parts', OrganismPartViewSet)
router.register(r'cell_types', CellTypeViewSet)
router.register(r'tissue_types', TissueTypeViewSet)
router.register(r'experiment_types', ExperimentTypeViewSet)
router.register(r'quantification_methods', QuantificationMethodViewSet)
router.register(r'raw_sample_column', RawSampleColumnViewSet)
router.register(r'differential_sample_column', DifferentialSampleColumnViewSet)
router.register(r'raw_data', RawDataViewSet)
router.register(r'differential_data', DifferentialAnalysisDataViewSet)
router.register(r'instruments', InstrumentViewSet)
router.register(r'diseases', DiseaseViewSet)
router.register(r'curtain', CurtainViewSet)
router.register(r'comparisons', ComparisonViewSet)
router.register(r'genenamemap', GeneNameMapViewSet)
router.register(r'lab_groups', LabGroupViewSet)
router.register(r'uniprot_record', UniprotRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('csrf/', CSRFTokenView.as_view(), name="csrf_token"),
    path('overview/', GetOverview.as_view(), name="overview"),
    path('user/', UserView.as_view(), name="user"),
    path('netphos/', NetPhosView.as_view(), name="netphos"),
    path('site-properties/', SitePropertiesView.as_view(), name="site_properties"),
    #path('accounts/', include('allauth.urls')),
    path('genemap-refresh/', UniprotRefreshView.as_view(), name="genemap_refresh"),
    path('rest-auth/google/', GoogleLogin2.as_view(), name='google_login'),
    path('rest-auth/orcid/', ORCIDOAUTHView.as_view(), name='orcid_login'),
] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

