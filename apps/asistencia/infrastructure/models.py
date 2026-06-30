import uuid
from django.db import models


class Attendance(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee     = models.ForeignKey('employees.Employee', on_delete=models.CASCADE,
                     related_name='attendances')
    work_date    = models.DateField()
    check_in     = models.DateTimeField(null=True, blank=True)
    check_out    = models.DateTimeField(null=True, blank=True)
    hours_worked = models.DecimalField(max_digits=4, decimal_places=2,
                     null=True, blank=True)
    extra_hours  = models.DecimalField(max_digits=4, decimal_places=2,
                     default=0)
    late_minutes = models.PositiveIntegerField(default=0)
    is_absence   = models.BooleanField(default=False)
    notes        = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attendance'
        unique_together = [('employee', 'work_date')]
        indexes = [
            models.Index(fields=['employee', 'work_date']),
            models.Index(fields=['work_date']),
        ]

    def calculate_hours(self) -> None:
        """Calcula horas trabajadas y extra al registrar salida."""
        if not self.check_in or not self.check_out:
            return
        delta = self.check_out - self.check_in
        total_minutes = delta.total_seconds() / 60
        standard_minutes = 480  # 8 horas

        self.hours_worked = round(total_minutes / 60, 2)

        if total_minutes > standard_minutes:
            self.extra_hours = round((total_minutes - standard_minutes) / 60, 2)


class LeaveRequest(models.Model):
    class LeaveType(models.TextChoices):
        VACATION = 'VACACIONES',    'Vacaciones'
        PERSONAL = 'PERSONAL',      'Permiso personal'
        MEDICAL  = 'MEDICO',        'Permiso médico'
        GRIEF    = 'DUELO',         'Duelo'
        OTHER    = 'OTRO',          'Otro'

    class Status(models.TextChoices):
        PENDING   = 'PENDIENTE',  'Pendiente'
        APPROVED  = 'APROBADA',   'Aprobada'
        REJECTED  = 'RECHAZADA',  'Rechazada'
        CANCELLED = 'CANCELADA',  'Cancelada'

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee     = models.ForeignKey('employees.Employee', on_delete=models.CASCADE,
                     related_name='leave_requests')
    leave_type   = models.CharField(max_length=20, choices=LeaveType.choices)
    start_date   = models.DateField()
    end_date     = models.DateField()
    total_days   = models.PositiveSmallIntegerField()
    reason       = models.TextField(blank=True)
    status       = models.CharField(max_length=20, choices=Status.choices,
                     default=Status.PENDING)
    reviewed_by  = models.ForeignKey('employees.Employee', null=True, blank=True,
                     on_delete=models.SET_NULL, related_name='reviewed_leaves')
    review_notes = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'leave_requests'
        indexes  = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]


class LeaveBalance(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee       = models.ForeignKey('employees.Employee', on_delete=models.CASCADE,
                       related_name='leave_balance')
    year           = models.PositiveSmallIntegerField()
    entitled_days  = models.DecimalField(max_digits=5, decimal_places=1)
    used_days      = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    pending_days   = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    remaining_days = models.DecimalField(max_digits=5, decimal_places=1)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'leave_balance'
        unique_together = [('employee', 'year')]


class License(models.Model):
    class LicenseType(models.TextChoices):
        DISABILITY  = 'INCAPACIDAD',       'Incapacidad médica'
        MATERNITY   = 'MATERNIDAD',        'Licencia de maternidad'
        PATERNITY   = 'PATERNIDAD',        'Licencia de paternidad'
        SPECIAL     = 'PERMISO_ESPECIAL',  'Permiso especial'
        UNPAID      = 'PERMISO_SIN_GOCE',  'Permiso sin goce de sueldo'

    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee      = models.ForeignKey('employees.Employee', on_delete=models.CASCADE,
                      related_name='licenses')
    license_type  = models.CharField(max_length=25, choices=LicenseType.choices)
    start_date    = models.DateField()
    end_date      = models.DateField()
    total_days    = models.PositiveSmallIntegerField()
    with_pay      = models.BooleanField(default=True)
    notes         = models.TextField(blank=True)
    registered_by = models.ForeignKey('authentication.User', null=True,
                      on_delete=models.SET_NULL)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'licenses'