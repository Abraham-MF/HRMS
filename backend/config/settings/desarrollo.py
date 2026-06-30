from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True

# SQLite local para desarrollo ultra-rápido (opcional)
# DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL  = '/media/'