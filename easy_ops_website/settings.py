"""
Django settings for easy_ops_website project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '28ta%!1(r3z17!xq4nh6-5!u_s-v37z!f#0!zt)jy61zwp4)a9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    #'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'UserManage',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'easy_ops_website.urls'

WSGI_APPLICATION = 'easy_ops_website.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
if 'SERVER_SOFTWARE' in os.environ:
    from sae.const import (
        MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
else:
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = '3306'
    MYSQL_USER = 'root'
    MYSQL_PASS = 'datacenter@secu'
    MYSQL_DB = 'easy_ops'

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE' : 'django.db.backends.mysql',
        'NAME' : MYSQL_DB,
        'USER' : MYSQL_USER,
        'PASSWORD' : MYSQL_PASS,
        'HOST' : MYSQL_HOST,
        'PORT' : MYSQL_PORT,
    },
    'cc' : {
        'ENGINE' : 'django.db.backends.mysql',
        'NAME' : 'center_control',
        'USER' : MYSQL_USER,
        'PASSWORD' : MYSQL_PASS,
        'HOST' : MYSQL_HOST,
        'PORT' : MYSQL_PORT,
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

#LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'utf-8'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

AUTH_USER_MODEL = 'UserManage.User'

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR,'static'),
)

#set TEMPLATE_DIRS
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

#TEMPLATE zh_CN
FILE_CHARSET='utf-8'
DEFAULT_CHARSET='utf-8'

#upload file's path
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

#redis host,port
REDIS_HOST = "192.168.235.129"
REDIS_PORT = "6379"

#Center Control SCP
DST_HOST = "192.168.235.134"
DST_USR = "root"
DST_PSW = "datacenter@secu"
SRC_WEB_DIR = "/data/web/easy_ops_website/media/cc/"
DST_NAS_DIR = "/tmp/"