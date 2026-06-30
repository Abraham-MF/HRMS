from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from core.permisos import IsAdminOrHR, IsAdminOnly
from core.paginacion import StandardResultsPagination
from ..infrastructure.models import Attendance, LeaveRequest, LeaveBalance, License
from apps.empleados.infrastructure.models import Employee
from .serializers import (
    AttendanceSerializer, CheckInSerializer, CheckOutSerializer,
    LeaveRequestSerializer, LeaveApprovalSerializer,
    LeaveBalanceSerializer, LicenseSerializer,
)


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class   = AttendanceSerializer
    permission_classes = [IsAdminOrHR]
    pagination_class   = StandardResultsPagination
    filterset_fields   = ['employee', 'work_date', 'is_absence']

    def get_queryset(self):
        return Attendance.objects.select_related('employee').all()

    @extend_schema(summary='Registrar entrada de un empleado', tags=['asistencia'])
    @action(detail=False, methods=['post'], url_path='check-in',
            permission_classes=[IsAuthenticated])
    def check_in(self, request):
        ser = CheckInSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        employee = Employee.objects.get(pk=ser.validated_data['employee_id'])
        today    = timezone.localdate()

        record, created = Attendance.objects.get_or_create(
            employee=employee,
            work_date=today,
            defaults={
                'check_in': timezone.now(),
                'notes':    ser.validated_data.get('notes', ''),
            }
        )
        if not created and record.check_in:
            return Response({'detail': 'Ya se registró la entrada de hoy.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not created:
            record.check_in = timezone.now()
            record.save()

        # Calcular retraso vs horario del empleado
        schedule = employee.schedule
        if schedule and schedule.monday_start:
            scheduled_start = timezone.datetime.combine(
                today, schedule.monday_start,
                tzinfo=timezone.get_current_timezone()
            )
            delta_minutes = (timezone.now() - scheduled_start).seconds // 60
            if delta_minutes > 0:
                record.late_minutes = delta_minutes
                record.save()

        return Response(AttendanceSerializer(record).data,
                        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @extend_schema(summary='Registrar salida de un empleado', tags=['asistencia'])
    @action(detail=False, methods=['post'], url_path='check-out',
            permission_classes=[IsAuthenticated])
    def check_out(self, request):
        ser = CheckInSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        employee = Employee.objects.get(pk=ser.validated_data['employee_id'])
        today    = timezone.localdate()

        try:
            record = Attendance.objects.get(employee=employee, work_date=today)
        except Attendance.DoesNotExist:
            return Response({'detail': 'No hay registro de entrada para hoy.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if record.check_out:
            return Response({'detail': 'Ya se registró la salida de hoy.'},
                            status=status.HTTP_400_BAD_REQUEST)

        record.check_out = timezone.now()
        record.notes     = ser.validated_data.get('notes', record.notes)
        record.calculate_hours()
        record.save()
        return Response(AttendanceSerializer(record).data)


class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class   = LeaveRequestSerializer
    pagination_class   = StandardResultsPagination
    filterset_fields   = ['employee', 'status', 'leave_type']

    def get_queryset(self):
        qs   = LeaveRequest.objects.select_related('employee', 'reviewed_by').all()
        user = self.request.user
        # Empleados solo ven sus propias solicitudes
        if hasattr(user, 'role') and user.role == 'EMPLOYEE' and user.employee:
            qs = qs.filter(employee=user.employee)
        return qs

    def get_permissions(self):
        if self.action in ['approve']:
            return [IsAdminOrHR()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # Si no viene employee, asigna el propio usuario
        if not serializer.validated_data.get('employee') and \
           hasattr(self.request.user, 'employee') and self.request.user.employee:
            serializer.save(employee=self.request.user.employee)
        else:
            serializer.save()

    @extend_schema(summary='Aprobar o rechazar una solicitud de permiso', tags=['asistencia'])
    @action(detail=True, methods=['post'], url_path='review',
            permission_classes=[IsAdminOrHR])
    def review(self, request, pk=None):
        leave = self.get_object()
        if leave.status != 'PENDIENTE':
            return Response({'detail': 'Solo se pueden revisar solicitudes pendientes.'},
                            status=status.HTTP_400_BAD_REQUEST)

        ser = LeaveApprovalSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        if ser.validated_data['action'] == 'approve':
            leave.status = 'APROBADA'
            # Descontar días del balance
            balance, _ = LeaveBalance.objects.get_or_create(
                employee=leave.employee,
                year=leave.start_date.year,
                defaults={'entitled_days': 15, 'remaining_days': 15},
            )
            if balance.remaining_days < leave.total_days:
                return Response({'detail': 'El empleado no tiene suficientes días disponibles.'},
                                status=status.HTTP_400_BAD_REQUEST)
            balance.used_days      += leave.total_days
            balance.remaining_days -= leave.total_days
            balance.save()
        else:
            leave.status = 'RECHAZADA'

        leave.reviewed_by  = request.user.employee if hasattr(request.user, 'employee') else None
        leave.review_notes = ser.validated_data.get('review_notes', '')
        leave.reviewed_at  = timezone.now()
        leave.save()
        return Response(LeaveRequestSerializer(leave).data)


class LeaveBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class   = LeaveBalanceSerializer
    permission_classes = [IsAdminOrHR]
    pagination_class   = StandardResultsPagination
    filterset_fields   = ['employee', 'year']

    def get_queryset(self):
        return LeaveBalance.objects.select_related('employee').all()


class LicenseViewSet(viewsets.ModelViewSet):
    serializer_class   = LicenseSerializer
    permission_classes = [IsAdminOrHR]
    pagination_class   = StandardResultsPagination
    filterset_fields   = ['employee', 'license_type']

    def get_queryset(self):
        return License.objects.select_related('employee').all()

    def perform_create(self, serializer):
        serializer.save(registered_by=self.request.user)
