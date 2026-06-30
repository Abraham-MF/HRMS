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
    ])),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/',   SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
