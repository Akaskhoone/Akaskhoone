from .base import *

DEBUG = False
ALLOWED_HOSTS = ['127.0.0.1', '192.168.11.190']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'akaskhoone',
        'USER': 'aasmpro',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=365),
}
