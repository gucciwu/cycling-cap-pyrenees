"""
Django settings for flex travels activity project.

Generated by 'django-admin startproject' using Django 2.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
import os

DEBUG = False

PYRENEES_CLUSTER = {'GROUP_NAME': 'PGD001', 'NODE_NAME': 'PND001'}

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOG_FILE_NAME = 'pyrenees_' + PYRENEES_CLUSTER['GROUP_NAME'] + '-' + PYRENEES_CLUSTER['NODE_NAME'] + '.log'
LOG_FILE_PATH = './'
LOG_FILE = LOG_FILE_PATH + LOG_FILE_NAME

STATIC_URL = 'http://pyrenees.cycling-cap.cn/static/'
STATIC_ROOT = '/pyrenees/data/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/pyrenees/data/media/'
MEDIA_PATH_AVATAR = 'avatars/'
MEDIA_PATH_TEMP = 'temp/'

FILE_PARSER = {
    'FIT_PARSER': '/pyrenees/tools/FitSDKRelease_21.22.00/java/FitCSVTool.jar',
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pyrenees',
        'USER': 'root',
        'PASSWORD': 'YourPassword',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    },
    'mongodb': {
        'NAME': 'pyrenees-test',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '27017',
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://172.16.0.9:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}


SITE = {
    'name': 'Pyrenees of Cycling-Cap',
    'root': 'http://pyrenees.cycling-cap.cn/'
}

ADMIN_SITE = {
    'site_title': SITE['name'] + ' Admin',
    'site_header': SITE['name'] + ' Administration',
    'index_title': SITE['name'] + ' Administration',
}

