"""
Django settings for purpleserver project.

Generated by 'django-admin startproject' using Django 3.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import importlib
from pathlib import Path
from decouple import config
from django.urls import reverse_lazy
from django.templatetags.static import static
from django.utils.functional import lazy
from django.core.management.utils import get_random_secret_key

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__ + '/../..'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default=get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG_MODE', default=True, cast=bool)

# custom env
WORK_DIR = config('WORK_DIR', default='')
Path(WORK_DIR).mkdir(parents=True, exist_ok=True)

USE_HTTPS = config('USE_HTTPS', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')
CORS_ORIGIN_ALLOW_ALL = True

with open(f"{BASE_DIR}/VERSION", "r") as v:
    VERSION = v.read()

# HTTPS configuration
if USE_HTTPS is True:
    global SECURE_SSL_REDIRECT
    global SECURE_PROXY_SSL_HEADER

    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Application definition

PURPLSHIP_CONF = [
    app for app in [
        {'app': 'purpleserver.core', 'module': 'purpleserver.core', 'urls': 'purpleserver.core.urls'},
        {'app': 'purpleserver.providers', 'module': 'purpleserver.providers', 'urls': 'purpleserver.providers.urls'},
        {'app': 'purpleserver.proxy', 'module': 'purpleserver.proxy', 'urls': 'purpleserver.proxy.urls'},
        {'app': 'purpleserver.manager', 'module': 'purpleserver.manager', 'urls': 'purpleserver.manager.urls'},
        {'app': 'purpleserver.client', 'module': 'purpleserver.client', 'urls': 'purpleserver.client.urls'},
        {'app': 'purpleserver.pricing', 'module': 'purpleserver.pricing'},
    ]
    if importlib.util.find_spec(app['module']) is not None
]

PURPLSHIP_APPS = [cfg['app'] for cfg in PURPLSHIP_CONF]
PURPLSHIP_URLS = [cfg['urls'] for cfg in PURPLSHIP_CONF if 'urls' in cfg]


DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

INSTALLED_APPS = [
    *PURPLSHIP_APPS,
    *DJANGO_APPS,

    'rest_framework',
    'rest_framework.authtoken',

    'oauth2_provider',
    'drf_yasg',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

HAS_CLIENT_APP = importlib.util.find_spec('purpleserver.client') is not None

ROOT_URLCONF = 'purpleserver.urls'
LOGOUT_REDIRECT_URL = '/login/' if HAS_CLIENT_APP else '/'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
OPEN_API_PATH = 'api/' if HAS_CLIENT_APP else ''


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'purpleserver', 'templates')
        ],
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

WSGI_APPLICATION = 'purpleserver.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DB_ENGINE = config('DATABASE_ENGINE', default='postgresql_psycopg2')

DATABASES = {
    'default': {
        'NAME': config('DATABASE_NAME', default='db'),
        'ENGINE': 'django.db.backends.{}'.format(DB_ENGINE),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'USER': config('DATABASE_USERNAME'),
        'HOST': config('DATABASE_HOST'),
        'PORT': config('DATABASE_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'purpleserver', 'static')
]


# Django REST framework

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    ),

    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ),

    'DEFAULT_THROTTLE_RATES': {
        'anon': '40/minute',
        'user': '60/minute'
    },

    'EXCEPTION_HANDLER': 'purpleserver.core.exceptions.custom_exception_handler',

    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
    ),

    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseFormParser',
        'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ),

    'JSON_UNDERSCOREIZE': {
        'no_underscore_before_number': True,
    },

    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}


# OAUTH2 config
static_lazy = lazy(static, str)

OAUTH2_CLIENT_ID = config('OAUTH2_CLIENT_ID', default=get_random_secret_key())
OAUTH2_CLIENT_SECRET = config('OAUTH2_CLIENT_SECRET', default=get_random_secret_key())
OAUTH2_APP_NAME = 'PurplShip OAuth2 provider'

OAUTH2_REDIRECT_URL = static_lazy('drf-yasg/swagger-ui-dist/oauth2-redirect.html')
OAUTH2_AUTHORIZE_URL = reverse_lazy('oauth2_provider:authorize')
OAUTH2_TOKEN_URL = reverse_lazy('oauth2_provider:token')


# OpenAPI config

SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'LOGIN_URL': reverse_lazy('admin:login'),
    'LOGOUT_URL': '/admin/logout',

    'DEFAULT_INFO': 'purpleserver.urls.swagger_info',

    'SECURITY_DEFINITIONS': {
        'Token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        },
        'OAuth2 password': {
            'flow': 'password',
            'scopes': {
                'read': 'Read everything.',
                'write': 'Write everything,',
            },
            'tokenUrl': OAUTH2_TOKEN_URL,
            'type': 'oauth2',
        },
    },
    'OAUTH2_REDIRECT_URL': OAUTH2_REDIRECT_URL,
    'OAUTH2_CONFIG': {
        'clientId': OAUTH2_CLIENT_ID,
        'clientSecret': OAUTH2_CLIENT_SECRET,
        'appName': OAUTH2_APP_NAME,
    },
}

REDOC_SETTINGS = {
    'LAZY_RENDERING': False,
    'HIDE_HOSTNAME': True
}

# Logging configuration

LOG_LEVEL = ('DEBUG' if DEBUG else config('LOG_LEVEL', default='INFO'))
DJANGO_LOG_LEVEL = ('INFO' if DEBUG else config('DJANGO_LOG_LEVEL', default='WARNING'))
LOG_FILE_DIR = config('LOG_PATH', default=WORK_DIR)
LOG_FILE_NAME = os.path.join(LOG_FILE_DIR, 'debug.log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_FILE_NAME,
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': DJANGO_LOG_LEVEL,
            'propagate': False,
        },
        'purplship': {
            'handlers': ['file', 'console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'purpleserver': {
            'handlers': ['file', 'console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}
