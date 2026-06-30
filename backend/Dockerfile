FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip

RUN pip install \
    Django \
    djangorestframework \
    djangorestframework-simplejwt \
    psycopg2-binary \
    gunicorn \
    django-filter \
    django-cors-headers \
    drf-spectacular \
    django-storages \
    boto3 \
    Pillow \
    celery \
    redis \
    django-celery-beat \
    python-dotenv \
    whitenoise \
    openpyxl \
    pandas

# Copiar TODO el proyecto (context debe ser la raíz)
COPY . .

EXPOSE 8000

# Entrypoint: migrate + collectstatic + gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4"]
