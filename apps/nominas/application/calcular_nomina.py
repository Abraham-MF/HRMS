from decimal import Decimal
from django.utils import timezone
from ..domain.nomina import PayrollCalculatorService
from ..infrastructure.models import PayrollPeriod, PayrollRecord
from apps.empleados.infrastructure.models import Employee
from apps.asistencia.infrastructure.models import Attendance


class CalculatePayrollUseCase:
    """
    Calcula la nómina de todos los empleados activos para un periodo dado.
    Si ya existe un recibo para ese (empleado, periodo) lo omite.
    """

    def __init__(self):
        self.calculator = PayrollCalculatorService()

    def execute(self, period_id: str, calculated_by_user) -> list[PayrollRecord]:
        period    = PayrollPeriod.objects.get(pk=period_id)
        employees = Employee.objects.filter(is_active=True).select_related('job_position')
        created   = []

        for emp in employees:
            if PayrollRecord.objects.filter(employee=emp, period=period).exists():
                continue

            # Horas extra en el periodo desde asistencia
            attendance_qs = Attendance.objects.filter(
                employee=emp,
                work_date__gte=period.start_date,
                work_date__lte=period.end_date,
            )
            extra_hours = sum(
                a.extra_hours for a in attendance_qs if a.extra_hours
            )
            extra_hours = Decimal(str(extra_hours))

            hourly_rate = emp.base_salary / Decimal('30') / Decimal('8')
            extra_hours_amount = self.calculator.calculate_extra_hours(
                hourly_rate, extra_hours
            ) if extra_hours > 0 else Decimal('0')

            result = self.calculator.calculate(
                base_salary=emp.base_salary,
                extra_hours_amount=extra_hours_amount,
                has_infonavit=True,
            )

            record = PayrollRecord.objects.create(
                employee=emp,
                period=period,
                base_salary=result.base_salary,
                extra_hours_amount=result.extra_hours_amount,
                bonuses=result.bonuses,
                commissions=result.commissions,
                other_income=result.other_income,
                gross_salary=result.gross_salary,
                isr_deduction=result.isr_deduction,
                imss_deduction=result.imss_deduction,
                infonavit_deduction=result.infonavit_deduction,
                loans_deduction=result.loans_deduction,
                other_deductions=result.other_deductions,
                total_deductions=result.total_deductions,
                net_salary=result.net_salary,
                extra_hours=extra_hours,
                has_infonavit=True,
                calculated_by=calculated_by_user,
            )
            created.append(record)

        return created


class ProcessPaymentUseCase:
    """Envía pagos al gateway bancario y marca recibos como PAGADO."""

    def __init__(self, banking_gateway):
        self.gateway = banking_gateway

    def execute(self, period_id: str) -> dict:
        records = PayrollRecord.objects.filter(
            period_id=period_id, status='APROBADO'
        ).select_related('employee')

        results = {'success': [], 'failed': []}
        for record in records:
            from ..infrastructure.bancario.gateway import PaymentRequest
            req = PaymentRequest(
                employee_id=str(record.employee.id),
                employee_name=record.employee.full_name,
                amount=record.net_salary,
                bank_name=record.bank_name or 'N/A',
                account_number=record.account_number or '0',
                clabe=record.clabe or '0' * 18,
                reference=f'NOM-{record.period_id}-{record.employee.employee_number}',
                period=str(record.period),
            )
            response = self.gateway.send_payment(req)
            if response.success:
                record.status         = 'PAGADO'
                record.transaction_id = response.transaction_id
                record.paid_at        = timezone.now()
                record.save()
                results['success'].append(record.id)
            else:
                results['failed'].append({'id': record.id, 'reason': response.message})

        return results
