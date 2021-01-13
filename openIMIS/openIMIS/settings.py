"""
Django settings for openIMIS project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""
import json
import os

from dotenv import load_dotenv
from .openimisapps import openimis_apps, get_locale_folders

load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


LOGGING = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'short': {
            'format': '%(name)s: %(message)s'
        }
    },
    'handlers': {
        'db-queries': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.environ.get("DB_QUERIES_LOG_FILE", 'db-queries.log'),
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 10,
            'formatter': 'standard',
        },
        'debug-log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.environ.get("DEBUG_LOG_FILE", 'debug.log'),
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 3,
            'formatter': 'standard',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'short'
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['db-queries'],
        },
        'openIMIS': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
        # GraphQL schema loading can be tricky and hide errors, use this to debug it
        # 'openIMIS.schema': {
        #     'level': 'DEBUG',
        #     'handlers': ['debug-log', 'console'],
        # },

    }
}


def SITE_ROOT():
    root = os.environ.get("SITE_ROOT", '')
    if (root == ''):
        return root
    elif (root.endswith('/')):
        return root
    else:
        return "%s/" % root


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY", 'chv^^7i_v3-04!rzu&qe#+h*a=%h(ib#5w9n$!f2q7%2$qp=zz')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", 'False').lower() == 'true'
# SECURITY WARNING: don't run without row security in production!
# Row security is dedicated to filter the data result sets according to users' right
# Example: user registered at a Health Facility should only see claims recorded for that Health Facility
ROW_SECURITY = os.environ.get("ROW_SECURITY", 'True').lower() == 'true'

if ("ALLOWED_HOSTS" in os.environ):
    ALLOWED_HOSTS = json.loads(os.environ["ALLOWED_HOSTS"])
else:
    ALLOWED_HOSTS = ['*']

# TEST_WITHOUT_MIGRATIONS_COMMAND = 'django_nose.management.commands.test.Command'
# TEST_RUNNER = 'core.test_utils.UnManagedModelTestRunner'
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'graphene_django',
    'test_without_migrations',
    'rest_framework',
    'rules',
    'rest_framework_rules',
	'health_check',                             # required
    'health_check.db',                          # stock Django health checkers
    'health_check.cache',
    'health_check.storage',
    'django_apscheduler',
    'channels'                                  # Websocket support
]
INSTALLED_APPS += openimis_apps()

AUTHENTICATION_BACKENDS = []
if bool(os.environ.get("REMOTE_USER_AUTHENTICATION", False)):
    AUTHENTICATION_BACKENDS += ['core.security.RemoteUserBackend']

AUTHENTICATION_BACKENDS += [
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
]

ANONYMOUS_USER_NAME = None

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'core.security.ObjectPermissions'
    ]
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware'
]
if bool(os.environ.get("REMOTE_USER_AUTHENTICATION", False)):
    MIDDLEWARE += [
        'core.security.RemoteUserMiddleware'
    ]
MIDDLEWARE += [
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'openIMIS.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'openIMIS.wsgi.application'

GRAPHENE = {
    'SCHEMA': 'openIMIS.schema.schema',
    'RELAY_CONNECTION_MAX_LIMIT': 100,
    'MIDDLEWARE': [
        'openIMIS.schema.GQLUserLanguageMiddleware'
    ]
}

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

if ("DB_OPTIONS" in os.environ):
    DATABASE_OPTIONS = json.loads(os.environ["DB_OPTIONS"])
elif (os.name == 'nt'):
    DATABASE_OPTIONS = {
        'driver': 'ODBC Driver 17 for SQL Server',
        'extra_params': "Persist Security Info=False;server=%s" % os.environ.get('DB_HOST'),
        'unicode_results': True
    }
else:
    DATABASE_OPTIONS = {
        'driver': 'ODBC Driver 17 for SQL Server',
        'unicode_results': True
    }

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'sql_server.pyodbc'),
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
        'OPTIONS': DATABASE_OPTIONS}
}

# Celery message broker configuration for RabbitMQ. One can also use Redis on AWS SQS
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "amqp://127.0.0.1")

# This scheduler config will:
# - Store jobs in the project database
# - Execute jobs in threads inside the application process, for production use, we could use a dedicated process
SCHEDULER_CONFIG = {
    "apscheduler.jobstores.default": {
        "class": "django_apscheduler.jobstores:DjangoJobStore"
    },
    'apscheduler.executors.processpool': {
        "type": "threadpool"
    },
}

SCHEDULER_AUTOSTART = os.environ.get("SCHEDULER_AUTOSTART", False)

# Normally, one creates a "scheduler" method that calls the appropriate scheduler.add_job but since we are in a
# modular architecture and calling only once from the core module, this has to be dynamic.
# This list will be called with scheduler.add_job() as specified:
# Note that the document implies that the time is local and follows DST but that seems false and in UTC regardless
SCHEDULER_JOBS = [
    {
        "method": "core.tasks.openimis_test_batch",
        "args": ["cron"],
        "kwargs": {"id": "openimis_test_batch", "minute": 16, "replace_existing": True},
    },
    # {
    #     "method": "policy.tasks.get_policies_for_renewal",
    #     "args": ["cron"],
    #     "kwargs": {"id": "openimis_renewal_batch", "hour": 8, "minute": 30, "replace_existing": True},
    # },
]
# This one is called directly with the scheduler object as first parameter. The methods can schedule things on their own
SCHEDULER_CUSTOM = [
    {
        "method": "core.tasks.sample_method",
        "args": ["sample"],
        "kwargs": {"sample_named": "param"},
    },
]


AUTH_USER_MODEL = 'core.User'

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-GB'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# List of places to look for translations, this could include an external translation module
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
] + get_locale_folders()

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_URL = "/%sstatic/" % SITE_ROOT()


ASGI_APPLICATION = "openIMIS.asgi.application"

# Django channels require redis server running, by default it use 127.0.0.1, port 6379
# docker run -p 6379:6379 -d redis:5
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(
                os.environ.get('REDIS_HOST', '127.0.0.1'),
                os.environ.get('REDIS_PORT',  6379)
            )],
        },
    },
}
