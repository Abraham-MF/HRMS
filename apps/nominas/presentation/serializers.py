from rest_framework import serializers
from ..infrastructure.models import PayrollPeriod, PayrollRecord


class PayrollPeriodSerializer(serializers.ModelSerializer):
    periodType = serializers.CharField(source='period_type')
    startDate  = serializers.DateField(source='start_date')
    endDate    = serializers.DateField(source='end_date')

    class Meta:
        model  = PayrollPeriod
        fields = ['id', 'periodType', 'startDate', 'endDate', 'status']
        read_only_fields = ['id', 'status']

    def validate(self, data):
        start = data.get('start_date')
        end   = data.get('end_date')
        if start and end and start >= end:
            raise serializers.ValidationError('La fecha de inicio debe ser anterior a la de fin.')
        return data


class PayrollRecordSerializer(serializers.ModelSerializer):
    employeeId         = serializers.UUIDField(source='employee_id', read_only=True)
    employeeName       = serializers.SerializerMethodField()
    periodId           = serializers.UUIDField(source='period_id', read_only=True)
    periodLabel        = serializers.SerializerMethodField()
    baseSalary         = serializers.DecimalField(source='base_salary',         max_digits=12, decimal_places=2)
    extraHours         = serializers.DecimalField(source='extra_hours',         max_digits=5,  decimal_places=2, read_only=True)
    extraHoursAmount   = serializers.DecimalField(source='extra_hours_amount',  max_digits=12, decimal_places=2, read_only=True)
    otherIncome        = serializers.DecimalField(source='other_income',        max_digits=12, decimal_places=2, read_only=True)
    grossSalary        = serializers.DecimalField(source='gross_salary',        max_digits=12, decimal_places=2, read_only=True)
    isrDeduction       = serializers.DecimalField(source='isr_deduction',       max_digits=12, decimal_places=2, read_only=True)
    imssDeduction      = serializers.DecimalField(source='imss_deduction',      max_digits=12, decimal_places=2, read_only=True)
    infonavitDeduction = serializers.DecimalField(source='infonavit_deduction', max_digits=12, decimal_places=2, read_only=True)
    loansDeduction     = serializers.DecimalField(source='loans_deduction',     max_digits=12, decimal_places=2, read_only=True)
    otherDeductions    = serializers.DecimalField(source='other_deductions',    max_digits=12, decimal_places=2, read_only=True)
    totalDeductions    = serializers.DecimalField(source='total_deductions',    max_digits=12, decimal_places=2, read_only=True)
    netSalary          = serializers.DecimalField(source='net_salary',          max_digits=12, decimal_places=2, read_only=True)
    calculatedAt       = serializers.DateTimeField(source='calculated_at', read_only=True)

    class Meta:
        model  = PayrollRecord
        fields = [
            'id', 'employeeId', 'employeeName', 'periodId', 'periodLabel',
            'baseSalary', 'extraHours', 'extraHoursAmount',
            'bonuses', 'commissions', 'otherIncome',
            'grossSalary', 'isrDeduction', 'imssDeduction', 'infonavitDeduction',
            'loansDeduction', 'otherDeductions', 'totalDeductions', 'netSalary',
            'status', 'calculatedAt',
        ]
        read_only_fields = [
            'id', 'employeeId', 'employeeName', 'periodId', 'periodLabel',
            'extraHours', 'extraHoursAmount', 'otherIncome',
            'grossSalary', 'isrDeduction', 'imssDeduction', 'infonavitDeduction',
            'loansDeduction', 'otherDeductions', 'totalDeductions', 'netSalary',
            'calculatedAt',
        ]

    def get_employeeName(self, obj):
        emp = obj.employee
        return f'{emp.first_name} {emp.last_name}' if emp else ''

    def get_periodLabel(self, obj):
        return str(obj.period)