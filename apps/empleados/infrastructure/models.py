import uuid
from django.db import models
from core.audit import AuditableMixin
from django.conf import settings


class Department(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name        = models.CharField(max_length=100)
    code        = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    parent      = models.ForeignKey('self', null=True, blank=True,
                    on_delete=models.SET_NULL, related_name='children')
    manager     = models.ForeignKey('Employee', null=True, blank=True,
                    on_delete=models.SET_NULL, related_name='managed_departments')
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'departments'
        ordering = ['name']

    def __str__(self):
        return self.name


class JobPosition(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title       = models.CharField(max_length=150)
    code        = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    department  = models.ForeignKey(Department, on_delete=models.PROTECT,
                    related_name='positions')
    min_salary  = models.DecimalField(max_digits=12, decimal_places=2,
                    null=True, blank=True)
    max_salary  = models.DecimalField(max_digits=12, decimal_places=2,
                    null=True, blank=True)
    is_active   = models.BooleanField(default=True)

    class Meta:
        db_table = 'job_positions'

    def __str__(self):
        return f'{self.title} — {self.department.name}'


class WorkSchedule(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name         = models.CharField(max_length=100)
    monday_start = models.TimeField(null=True, blank=True)
    monday_end   = models.TimeField(null=True, blank=True)
    friday_start = models.TimeField(null=True, blank=True)
    friday_end   = models.TimeField(null=True, blank=True)
    weekly_hours = models.PositiveSmallIntegerField(default=40)
    is_active    = models.BooleanField(default=True)

    class Meta:
        db_table = 'work_schedules'

    def __str__(self):
        return self.name


class Employee(AuditableMixin, models.Model):
    class Status(models.TextChoices):
        ACTIVE    = 'ACTIVO',     'Activo'
        INACTIVE  = 'BAJA',       'Baja'
        SUSPENDED = 'SUSPENDIDO', 'Suspendido'
        VACATION  = 'VACACIONES', 'En vacaciones'

    class ContractType(models.TextChoices):
        INDEFINITE   = 'INDEFINIDO',   'Contrato indefinido'
        FIXED        = 'DETERMINADO',  'Contrato por tiempo determinado'
        PROFESSIONAL = 'HONORARIOS',   'Honorarios profesionales'

    class Gender(models.TextChoices):
        MALE       = 'MASCULINO',  'Masculino'
        FEMALE     = 'FEMENINO',   'Femenino'
        NON_BINARY = 'NO_BINARIO', 'No binario'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_number = models.CharField(max_length=20, unique=True)
    first_name      = models.CharField(max_length=100)
    last_name       = models.CharField(max_length=100)
    curp            = models.CharField(max_length=18, unique=True)
    rfc             = models.CharField(max_length=13, unique=True)
    birth_date      = models.DateField()
    gender          = models.CharField(max_length=20, choices=Gender.choices)
    marital_status  = models.CharField(max_length=20, blank=True)
    nationality     = models.CharField(max_length=60, default='Mexicana')
    address         = models.CharField(max_length=255, blank=True)
    city            = models.CharField(max_length=100, blank=True)
    state           = models.CharField(max_length=100, blank=True)
    postal_code     = models.CharField(max_length=5, blank=True)
    phone           = models.CharField(max_length=15, blank=True)
    email           = models.EmailField(unique=True)
    department      = models.ForeignKey(Department, on_delete=models.PROTECT,
                        related_name='employees')
    job_position    = models.ForeignKey(JobPosition, on_delete=models.PROTECT,
                        related_name='employees')
    supervisor      = models.ForeignKey('self', null=True, blank=True,
                        on_delete=models.SET_NULL, related_name='subordinates')
    schedule        = models.ForeignKey(WorkSchedule, null=True, blank=True,
                        on_delete=models.SET_NULL)
    hire_date       = models.DateField()
    contract_type   = models.CharField(max_length=20, choices=ContractType.choices)
    base_salary     = models.DecimalField(max_digits=12, decimal_places=2)
    employee_status = models.CharField(max_length=20, choices=Status.choices,
                        default=Status.ACTIVE)
    is_active       = models.BooleanField(default=True)
    deleted_at      = models.DateTimeField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employees'
        indexes = [
            models.Index(fields=['department', 'is_active'],   name='idx_emp_dept_active'),
            models.Index(fields=['employee_status'],            name='idx_emp_status'),
            models.Index(fields=['supervisor'],                 name='idx_emp_supervisor'),
        ]
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.employee_number} — {self.first_name} {self.last_name}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class EmploymentHistory(models.Model):
    class ChangeType(models.TextChoices):
        SALARY_CHANGE     = 'SALARY_CHANGE',     'Cambio salarial'
        DEPARTMENT_CHANGE = 'DEPARTMENT_CHANGE',  'Cambio de departamento'
        POSITION_CHANGE   = 'POSITION_CHANGE',    'Cambio de cargo'
        PROMOTION         = 'PROMOTION',          'Ascenso'
        TRANSFER          = 'TRANSFER',           'Transferencia'
        REHIRE            = 'REHIRE',             'Reingreso'
        STATUS_CHANGE     = 'STATUS_CHANGE',      'Cambio de estatus'

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee       = models.ForeignKey(Employee, on_delete=models.CASCADE,
                       related_name='employment_history')
    change_type    = models.CharField(max_length=30, choices=ChangeType.choices)
    previous_value = models.CharField(max_length=255, blank=True)
    new_value      = models.CharField(max_length=255, blank=True)
    notes          = models.TextField(blank=True)
    changed_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    null=True,
    blank=True,
    on_delete=models.SET_NULL
)
    changed_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'employment_history'
        ordering = ['-changed_at']