"""
Django settings for celsusdjango project.

Generated by 'django-admin startproject' using Django 4.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", 'django-insecure-56n6z$55fer(z9c+=x0e117u6y=t_k-@d_!z-k&5f9x*nt)_hu')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'celsus.apps.CelsusConfig',
    'channels',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',
    'django_sendfile',
    'allauth',
    'allauth.account',
    'dj_rest_auth.registration',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'dbbackup',
    'request',
]

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'request.middleware.RequestMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'celsusdjango.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'celsusdjango.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

ASGI_APPLICATION = 'celsusdjango.asgi.application'
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"
MEDIA_URL = ''
MEDIA_ROOT = BASE_DIR / "media/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

CORS_EXPOSED_HEADERS = [
    "Set-Cookie"
]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "withCredentials",
    "http_x_xsrf_token"
]
CORS_ORIGIN_WHITELIST = (
    'http://localhost:4200',
    'http://localhost:49537',
    'http://curtain.proteo.info',
    'http://curtainptm.proteo.info',
)
CSRF_USE_SESSIONS = False
CSRF_COOKIE_HTTPONLY = False  # this is the default, and should be kept this way
CSRF_COOKIE_NAME = 'XSRF-TOKEN'
CSRF_HEADER_NAME = 'HTTP_X_XSRF_TOKEN'

SPECTACULAR_SETTINGS = {
    'TITLE': 'Celsus Open API',
    'DESCRIPTION': 'A project for open proteomics data communication',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # OTHER SETTINGS
}

SENDFILE_BACKEND = "django_sendfile.backends.simple"
SENDFILE_ROOT = os.environ.get("DJANGO_MEDIA_ROOT", "D:/PycharmProjects/celsusdjango/media")

NETPHOS_WEB_URL = os.environ.get("NETPHOS_WEB_URL", "http://netphos:8000/api/netphos/predict")


SITE_ID = 1

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        'APP': {
            'client_id': os.environ.get('GOOGLE_OAUTH_CLIENT_ID', 'resorc'),
            'secret': os.environ.get('GOOGLE_OAUTH_SECRET', 'resorc'),
        }
    }
}


ORCID = {
    'client_id': os.environ.get('ORCID_OAUTH_CLIENT_ID', 'resorc'),
    'secret': os.environ.get('ORCID_OAUTH_SECRET', 'resorc'),
}


Q_CLUSTER = {
    'name': 'cactuscluster',
    'retry': 3601,
    'workers': 4,
    'recycle': 500,
    'timeout': 3600,
    'compress': True,
    'save_limit': 250,
    'queue_limit': 500,
    'cpu_affinity': 1,
    'label': 'cactus-q',
    'redis': {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 0,
    }
}

if os.environ.get("Q_CLUSTER_REDIS_HOST"):
    Q_CLUSTER['redis']['host'] = os.environ.get("Q_CLUSTER_REDIS_HOST")

if os.environ.get("Q_CLUSTER_REDIS_PASSWORD"):
    Q_CLUSTER['redis']['password'] = os.environ.get("Q_CLUSTER_REDIS_PASSWORD")

CURTAIN_ALLOW_NON_STAFF_DELETE = False
if os.environ.get("CURTAIN_ALLOW_NON_STAFF_DELETE"):
    v = int(os.environ.get("CURTAIN_ALLOW_NON_STAFF_DELETE"))
    if v == 1:
        CURTAIN_ALLOW_NON_STAFF_DELETE = True
    else:
        CURTAIN_ALLOW_NON_STAFF_DELETE = False

CURTAIN_ALLOW_NON_USER_POST = False
if os.environ.get("CURTAIN_ALLOW_NON_USER_POST"):
    v = int(os.environ.get("CURTAIN_ALLOW_NON_USER_POST"))
    if v == 1:
        CURTAIN_ALLOW_NON_USER_POST = True
    else:
        CURTAIN_ALLOW_NON_USER_POST = False

CURTAIN_DEFAULT_USER_LINK_LIMIT = 0
if os.environ.get("CURTAIN_DEFAULT_USER_LINK_LIMIT"):
    v = int(os.environ.get("CURTAIN_DEFAULT_USER_LINK_LIMIT"))
    if v > 0:
        CURTAIN_DEFAULT_USER_LINK_LIMIT = v

CURTAIN_DEFAULT_USER_CAN_POST = True
if os.environ.get("CURTAIN_DEFAULT_USER_CAN_POST"):
    v = int(os.environ.get("CURTAIN_DEFAULT_USER_CAN_POST"))
    if v == 1:
        CURTAIN_DEFAULT_USER_CAN_POST = True
    else:
        CURTAIN_DEFAULT_USER_CAN_POST = False
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': '/app/backup'}



if os.environ.get('POSTGRES_DB'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_NAME'),
            'USER': os.environ.get('POSTGRES_USER'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
            'HOST': os.environ.get('POSTGRES_HOST', 'db'),
            'PORT': int(os.environ.get('POSTGRES_PORT', '5432')),

        }
    }

    if os.environ.get('POSTGRES_SSL', '0') == '1':
        DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}

if os.environ.get("WORKDB_PROFILE") == "production":
    DEBUG = False


    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
                "rest_framework.renderers.JSONRenderer",
            )
    ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "http://localhost,http://127.0.0.1").split(",")
    CORS_ORIGIN_WHITELIST = os.environ.get("DJANGO_CORS_WHITELIST").split(",")
    MEDIA_ROOT = os.environ.get("DJANGO_MEDIA_ROOT")
    DBBACKUP_STORAGE_OPTIONS = {'location': os.environ.get("DBBACKUP_STORAGE_LOCATION")}
    DBBACKUP_CONNECTORS = {
        'default': {
            'dump_cmd': 'pg_dump --no-owner'
        }
    }
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [f"redis://:{Q_CLUSTER['redis']['password']}@{Q_CLUSTER['redis']['host']}:{Q_CLUSTER['redis']['port']}/{Q_CLUSTER['redis']['db']}"],
                "symmetric_encryption_keys": [SECRET_KEY]
            },
        },
    }

