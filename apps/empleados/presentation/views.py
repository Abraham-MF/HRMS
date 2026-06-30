# apps/empleados/presentation/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter

from core.permisos import IsAdminOrHR, IsAdminOnly, IsSelfOrAdminOrHR
from core.paginacion import StandardResultsPagination
from ..infrastructure.models import Employee, Department, JobPosition, EmploymentHistory
from ..infrastructure.repositorio import DjangoEmployeeRepository
from ..application.creacion_emp import CreateEmployeeUseCase
from ..application.actu_emp import UpdateEmployeeUseCase
from ..application.desactivar_emp import DeactivateEmployeeUseCase
from ..application.datos import CreateEmployeeDTO, UpdateEmployeeDTO
from .serializers import (
    EmployeeListSerializer, EmployeeDetailSerializer,
    EmploymentHistorySerializer, DepartmentSerializer, JobPositionSerializer
)


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para gestión de empleados.
    CRUD + acciones adicionales para historial, baja y reactivación.
    """
    pagination_class = StandardResultsPagination
    filter_backends  = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields    = ['first_name', 'last_name', 'employee_number', 'email']
    ordering_fields  = ['last_name', 'hire_date', 'base_salary', 'created_at']
    ordering         = ['last_name']

    def get_queryset(self):
        qs = Employee.objects.select_related(
            'department', 'job_position', 'supervisor', 'schedule'
        ).filter(is_active=True)

        user = self.request.user
        if user.role == 'SUPERVISOR' and user.employee:
            qs = qs.filter(supervisor=user.employee)
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        return EmployeeDetailSerializer

    def get_permissions(self):
        if self.action in ['destroy', 'deactivate']:
            return [IsAdminOnly()]
        if self.action in ['create', 'update', 'partial_update']:
            return [IsAdminOrHR()]
        return [IsSelfOrAdminOrHR()]

    @extend_schema(
        summary='Listar empleados',
        description='Retorna listado paginado con filtros por departamento, cargo y estatus.',
        parameters=[
            OpenApiParameter('department_id', str, description='UUID del departamento'),
            OpenApiParameter('employee_status', str, description='ACTIVO|BAJA|SUSPENDIDO'),
            OpenApiParameter('search', str, description='Búsqueda por nombre o número'),
        ],
        tags=['employees']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary='Crear empleado', tags=['employees'])
    def create(self, request, *args, **kwargs):
        serializer = EmployeeDetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        repo = DjangoEmployeeRepository()
        use_case = CreateEmployeeUseCase(repo)

        dto = CreateEmployeeDTO(**serializer.validated_data)
        try:
            result = use_case.execute(dto)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'id': result.id, 'employee_number': result.employee_number,
                         'full_name': result.full_name},
                        status=status.HTTP_201_CREATED)

    @extend_schema(summary='Dar de baja empleado (borrado lógico)', tags=['employees'])
    def destroy(self, request, *args, **kwargs):
        repo = DjangoEmployeeRepository()
        use_case = DeactivateEmployeeUseCase(repo)
        try:
            use_case.execute(str(kwargs['pk']))
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(summary='Historial laboral del empleado', tags=['employees'])
    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        employee = self.get_object()
        history  = EmploymentHistory.objects.filter(
            employee=employee
        ).order_by('-changed_at')
        serializer = EmploymentHistorySerializer(history, many=True)
        return Response(serializer.data)

    @extend_schema(summary='Reactivar empleado dado de baja', tags=['employees'])
    @action(detail=True, methods=['post'], url_path='reactivate',
            permission_classes=[IsAdminOnly])
    def reactivate(self, request, pk=None):
        try:
            employee = Employee.objects.get(pk=pk)
            employee.is_active       = True
            employee.employee_status = 'ACTIVO'
            employee.deleted_at      = None
            employee.save()
            return Response({'detail': 'Empleado reactivado correctamente.'})
        except Employee.DoesNotExist:
            return Response({'detail': 'Empleado no encontrado.'},
                            status=status.HTTP_404_NOT_FOUND)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset           = Department.objects.filter(is_active=True).order_by('name')
    serializer_class   = DepartmentSerializer
    permission_classes = [IsAdminOnly]
    filter_backends    = [filters.SearchFilter]
    search_fields      = ['name', 'code']

    @extend_schema(tags=['employees'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class JobPositionViewSet(viewsets.ModelViewSet):
    queryset           = JobPosition.objects.select_related('department').filter(is_active=True)
    serializer_class   = JobPositionSerializer
    permission_classes = [IsAdminOrHR]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields   = ['department']
    search_fields      = ['title', 'code']

    @extend_schema(tags=['employees'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
