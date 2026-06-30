from pathlib import Path
from datetime import timedelta
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# CONFIGURACIÓN GENERAL
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

DEBUG = False

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

# APLICACIONES
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "storages",
    "django_celery_beat",
]

LOCAL_APPS = [
    "apps.authentication",
    "apps.empleados",
    "apps.nominas",
    "apps.asistencia",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # Middleware propio
    "core.audit.AuditMiddleware",
]

# URLS
ROOT_URLCONF = "config.urls"

# MODELO DE USUARIO
AUTH_USER_MODEL = "authentication.User"

# BASE DE DATOS
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "hrms_db"),
        "USER": os.environ.get("DB_USER", "hrms_user"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        "OPTIONS": {
            "options": "-c default_transaction_isolation=serializable"
        },
        "CONN_MAX_AGE": 60,
    }
}

# CACHE (REDIS)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get(
            "REDIS_URL",
            "redis://redis:6379/0",
        ),
    }
}

# JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# DJANGO REST FRAMEWORK
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),

    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),

    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),

    "DEFAULT_PAGINATION_CLASS": "core.paginacion.StandardResultsPagination",

    "PAGE_SIZE": 20,

    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",

    "EXCEPTION_HANDLER": "core.ecepciones.custom_exception_handler",

    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),

    "DEFAULT_THROTTLE_RATES": {
        "anon": "20/minute",
        "user": "100/minute",
    },
}

# CELERY

CELERY_BROKER_URL = os.environ.get(
    "REDIS_URL",
    "redis://redis:6379/1",
)

CELERY_RESULT_BACKEND = os.environ.get(
    "REDIS_URL",
    "redis://redis:6379/1",
)

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

CELERY_TIMEZONE = "America/Mexico_City"

# ALMACENAMIENTO (MINIO / S3)

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

AWS_ACCESS_KEY_ID = os.environ.get("MINIO_ROOT_USER")
AWS_SECRET_ACCESS_KEY = os.environ.get("MINIO_ROOT_PASSWORD")

AWS_STORAGE_BUCKET_NAME = os.environ.get(
    "MINIO_BUCKET",
    "hrms-documents",
)

AWS_S3_ENDPOINT_URL = os.environ.get(
    "MINIO_ENDPOINT",
    "http://minio:9000",
)

AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = "private"

AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 3600

# SWAGGER / OPENAPI

SPECTACULAR_SETTINGS = {
    "TITLE": "HRMS API",
    "DESCRIPTION": "Sistema de Gestión de Recursos Humanos",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "TAGS": [
        {
            "name": "auth",
            "description": "Autenticación y JWT",
        },
        {
            "name": "employees",
            "description": "Gestión de empleados",
        },
        {
            "name": "payroll",
            "description": "Nómina",
        },
        {
            "name": "attendance",
            "description": "Asistencia",
        },
    ],
}

#INTERNACIONALIZACIÓN
LANGUAGE_CODE = "es-mx"

TIME_ZONE = "America/Mexico_City"

USE_I18N = True
USE_TZ = True

#SEGURIDAD
X_FRAME_OPTIONS = "DENY"

SECURE_CONTENT_TYPE_NOSNIFF = True