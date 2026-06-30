from datetime import date, timedelta

import django_filters
from django.utils import timezone
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter

from core.permisos import IsAdminOrHR
from core.paginacion import StandardResultsPagination
from ..infrastructure.models import EmployeeDocument
from .serializers import EmployeeDocumentSerializer


class EmployeeDocumentFilter(django_filters.FilterSet):
    # Alias en camelCase para que coincida con lo que envía el frontend
    # (?employeeId=<uuid>&category=<...>) en vez del nombre interno del campo.
    employeeId = django_filters.UUIDFilter(field_name='employee_id')

    class Meta:
        model  = EmployeeDocument
        fields = ['employeeId', 'category']


class EmployeeDocumentViewSet(viewsets.ModelViewSet):
    """
    Almacenamiento de documentos importantes del personal:
    contratos, certificados, identificaciones, comprobantes, etc.

    Solo Administrador y Recursos Humanos pueden ver, subir y eliminar
    documentos — son datos sensibles del expediente del empleado.
    """
    serializer_class   = EmployeeDocumentSerializer
    permission_classes = [IsAdminOrHR]
    pagination_class   = StandardResultsPagination
    filter_backends     = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class      = EmployeeDocumentFilter
    search_fields        = ['title', 'notes', 'employee__first_name', 'employee__last_name']
    ordering_fields     = ['uploaded_at', 'expires_at', 'title']
    ordering            = ['-uploaded_at']

    def get_queryset(self):
        qs = EmployeeDocument.objects.select_related(
            'employee', 'uploaded_by'
        ).filter(is_active=True)

        status_filter = self.request.query_params.get('status')
        today = date.today()
        if status_filter == 'VENCIDO':
            qs = qs.filter(expires_at__lt=today)
        elif status_filter == 'POR_VENCER':
            qs = qs.filter(expires_at__gte=today,
                            expires_at__lte=today + timedelta(days=30))
        elif status_filter == 'VIGENTE':
            qs = qs.filter(expires_at__gt=today + timedelta(days=30))

        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @extend_schema(
        summary='Listar documentos del personal',
        description='Listado paginado con filtros por empleado, categoría y '
                    'estatus de vencimiento (VIGENTE|POR_VENCER|VENCIDO).',
        parameters=[
            OpenApiParameter('employeeId', str, description='UUID del empleado'),
            OpenApiParameter('category', str, description='Categoría del documento'),
            OpenApiParameter('status', str, description='VIGENTE|POR_VENCER|VENCIDO'),
            OpenApiParameter('search', str, description='Búsqueda por título o empleado'),
        ],
        tags=['documents'],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary='Subir documento', tags=['documents'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(summary='Eliminar documento (borrado lógico)', tags=['documents'])
    def destroy(self, request, *args, **kwargs):
        document = self.get_object()
        document.is_active  = False
        document.deleted_at = timezone.now()
        document.save(update_fields=['is_active', 'deleted_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary='Documentos próximos a vencer o vencidos',
        description='Devuelve documentos vencidos o que vencen en los próximos 30 días.',
        tags=['documents'],
    )
    @action(detail=False, methods=['get'], url_path='expiring')
    def expiring(self, request):
        today = date.today()
        qs = self.get_queryset().filter(
            expires_at__isnull=False,
            expires_at__lte=today + timedelta(days=30),
        ).order_by('expires_at')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
