import os
from .base import *

DEBUG = False
# Lista de dominios separados por comas en la variable ALLOWED_HOSTS (p. ej. "urbanfield.es,www.urbanfield.es")
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', 'localhost').split(',') if h.strip()]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

STATIC_ROOT = BASE_DIR / 'staticfiles'  # Donde collectstatic agrupa los estáticos para Nginx