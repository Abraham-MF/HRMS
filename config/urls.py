from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/', include([
        path('auth/',        include('apps.authentication.presentation.urls')),
        path('employees/',   include('apps.empleados.presentation.urls')),
        path('payroll/',     include('apps.nominas.presentation.urls')),
        path('attendance/',  include('apps.asistencia.presentation.urls')),
        path('documents/',   include('apps.documentos.presentation.urls')),
        path('reports/',     include('apps.reportes.presentacion.urls')),
    ])),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/',   SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Servir documentos subidos (MEDIA) en desarrollo. En producción los archivos
# se sirven directamente desde S3/MinIO con URLs firmadas (ver
# config/settings/principal.py), por lo que esto no aplica ahí.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)