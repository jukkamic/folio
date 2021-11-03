"""
NOTE 
The API KEY settings must be included in my_settings.py file (not included in Git)
"""
from pathlib import Path
from . import my_settings
import os

CRYPTOPANIC_AUTH = my_settings.CRYPTOPANIC_AUTH
BINANCE_API_KEY = my_settings.BINANCE_API_KEY
BINANCE_API_SECRET = my_settings.BINANCE_API_SECRET
ETHERSCAN_API_KEY = my_settings.ETHERSCAN_API_KEY
KUCOIN_API_KEY = my_settings.KUCOIN_API_KEY
KUCOIN_API_SECRET = my_settings.KUCOIN_API_SECRET
KUCOIN_API_PASSPHRASE = my_settings.KUCOIN_API_PASSPHRASE

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = my_settings.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['folio.kotkis.fi',
                 '192.168.1.235',
#		 '54.195.99.44',
		 '127.0.0.1',
		 'localhost']

#ALLOWED_HOSTS = ['*']
#CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOWED_ORIGINS = ['http://localhost:3000',
#			'http://54.195.99.44:80',
                       'http://folio.kotkis.fi',
                       'https://folio.kotkis.fi',
                       'http://127.0.0.1:3000',
                       'http://192.168.1.235:3000',
                       'http://192.168.1.235:5000',
                       'http://localhost:5000']

# Application definition

INSTALLED_APPS = [
    'corsheaders',
    'clearcache',    
    'django.contrib.admin',
    'rest_framework',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mybin.apps.MybinConfig',
    'news',
    'blog'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wallet.urls'

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

WSGI_APPLICATION = 'wallet.wsgi.application'

CACHES = {
   'default': {
      'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
      'LOCATION': os.path.join(BASE_DIR, "django_cache"),
   }
}

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(BASE_DIR / 'db.sqlite3'),
    }
}

# Note the str() at NAME: BASE_DIR ... A bug fix.


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = {
#    'wallet.auth0backend.Auth0',
#    'django.contrib.auth.backends.ModelBackend'
    'django.contrib.auth.backends.ModelBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

JWT_AUTH = {
    'JWT_PAYLOAD_GET_USERNAME_HANDLER':
        'wallet.utils.jwt_get_username_from_payload_handler',
    'JWT_DECODE_HANDLER':
        'wallet.utils.jwt_decode_token',
    'JWT_ALGORITHM': 'RS256',
    'JWT_AUDIENCE': 'https://folio.kotkis.fi/',
    'JWT_ISSUER': 'https://dev-88-mri1m.us.auth0.com/',
#    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
}
# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
