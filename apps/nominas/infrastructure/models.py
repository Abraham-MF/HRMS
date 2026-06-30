import uuid
from django.db import models


class PayrollPeriod(models.Model):
    class PeriodType(models.TextChoices):
        WEEKLY     = 'SEMANAL',    'Semanal'
        BIWEEKLY   = 'QUINCENAL',  'Quincenal'
        MONTHLY    = 'MENSUAL',    'Mensual'

    class Status(models.TextChoices):
        OPEN   = 'ABIERTO',  'Abierto'
        CLOSED = 'CERRADO',  'Cerrado'
        PAID   = 'PAGADO',   'Pagado'

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    period_type = models.CharField(max_length=15, choices=PeriodType.choices,
                    default=PeriodType.BIWEEKLY)
    start_date  = models.DateField()
    end_date    = models.DateField()
    status      = models.CharField(max_length=15, choices=Status.choices,
                    default=Status.OPEN)
    created_at  = models.DateTimeField(auto_now_add=True)
    closed_at   = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'payroll_periods'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.period_type} {self.start_date} – {self.end_date}'


class PayrollRecord(models.Model):
    class Status(models.TextChoices):
        CALCULATED = 'CALCULADO', 'Calculado'
        APPROVED   = 'APROBADO',  'Aprobado'
        PAID       = 'PAGADO',    'Pagado'
        CANCELLED  = 'CANCELADO', 'Cancelado'

    id                  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee            = models.ForeignKey('employees.Employee', on_delete=models.PROTECT,
                            related_name='payroll_records')
    period              = models.ForeignKey(PayrollPeriod, on_delete=models.PROTECT,
                            related_name='records')
    # Ingresos
    base_salary         = models.DecimalField(max_digits=12, decimal_places=2)
    extra_hours_amount  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonuses             = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    commissions         = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_income        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gross_salary        = models.DecimalField(max_digits=12, decimal_places=2)
    # Deducciones
    isr_deduction       = models.DecimalField(max_digits=10, decimal_places=2)
    imss_deduction      = models.DecimalField(max_digits=10, decimal_places=2)
    infonavit_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    loans_deduction     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_deductions    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deductions    = models.DecimalField(max_digits=12, decimal_places=2)
    net_salary          = models.DecimalField(max_digits=12, decimal_places=2)
    # Control
    status              = models.CharField(max_length=15, choices=Status.choices,
                            default=Status.CALCULATED)
    bank_name           = models.CharField(max_length=100, blank=True)
    account_number      = models.CharField(max_length=30, blank=True)
    clabe               = models.CharField(max_length=18, blank=True)
    transaction_id      = models.CharField(max_length=100, blank=True)
    has_infonavit       = models.BooleanField(default=False)
    extra_hours         = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    calculated_at       = models.DateTimeField(auto_now_add=True)
    approved_at         = models.DateTimeField(null=True, blank=True)
    paid_at             = models.DateTimeField(null=True, blank=True)
    calculated_by       = models.ForeignKey('authentication.User', null=True,
                            on_delete=models.SET_NULL, related_name='calculated_payrolls')

    class Meta:
        db_table        = 'payroll_records'
        unique_together = [('employee', 'period')]
        ordering        = ['-calculated_at']

    def __str__(self):
        return f'{self.employee} — {self.period}'
