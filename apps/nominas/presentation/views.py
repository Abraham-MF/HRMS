from decimal import Decimal
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from core.permisos import IsAdminOrHR, IsAdminOnly
from core.paginacion import StandardResultsPagination
from ..infrastructure.models import PayrollPeriod, PayrollRecord
from ..infrastructure.bancario.gateway import MockBankingGateway
from ..application.calcular_nomina import CalculatePayrollUseCase, ProcessPaymentUseCase
from .serializers import PayrollPeriodSerializer, PayrollRecordSerializer


class PayrollPeriodViewSet(viewsets.ModelViewSet):
    queryset           = PayrollPeriod.objects.all()
    serializer_class   = PayrollPeriodSerializer
    permission_classes = [IsAdminOrHR]
    pagination_class   = StandardResultsPagination

    @extend_schema(summary='Calcular nómina de todos los empleados activos para este periodo',
                   tags=['nominas'])
    @action(detail=True, methods=['post'], url_path='calculate')
    def calculate(self, request, pk=None):
        period = self.get_object()
        if period.status == 'CERRADO':
            return Response({'detail': 'El periodo ya está cerrado.'},
                            status=status.HTTP_400_BAD_REQUEST)

        use_case = CalculatePayrollUseCase()
        try:
            records = use_case.execute(str(period.id), request.user)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'detail': f'{len(records)} recibos calculados correctamente.',
            'period_id': str(period.id),
            'records_created': len(records),
        })

    @extend_schema(summary='Aprobar todos los recibos CALCULADO del periodo', tags=['nominas'])
    @action(detail=True, methods=['post'], url_path='approve',
            permission_classes=[IsAdminOnly])
    def approve(self, request, pk=None):
        period  = self.get_object()
        updated = PayrollRecord.objects.filter(
            period=period, status='CALCULADO'
        ).update(status='APROBADO', approved_at=timezone.now())
        return Response({'detail': f'{updated} recibos aprobados.'})

    @extend_schema(summary='Enviar pagos al gateway bancario', tags=['nominas'])
    @action(detail=True, methods=['post'], url_path='pay',
            permission_classes=[IsAdminOnly])
    def pay(self, request, pk=None):
        period = self.get_object()
        if period.status == 'PAGADO':
            return Response({'detail': 'El periodo ya fue pagado.'},
                            status=status.HTTP_400_BAD_REQUEST)

        use_case = ProcessPaymentUseCase(MockBankingGateway())
        results  = use_case.execute(str(period.id))

        if not results['failed']:
            period.status    = 'PAGADO'
            period.closed_at = timezone.now()
            period.save()

        return Response({
            'success_count': len(results['success']),
            'failed_count':  len(results['failed']),
            'failed':        results['failed'],
        })


class PayrollRecordViewSet(viewsets.ModelViewSet):
    serializer_class   = PayrollRecordSerializer
    permission_classes = [IsAdminOrHR]
    pagination_class   = StandardResultsPagination
    filterset_fields   = ['period', 'employee', 'status']

    def get_queryset(self):
        return PayrollRecord.objects.select_related(
            'employee', 'period'
        ).all()

    @extend_schema(summary='Recalcular un recibo individual con ajustes manuales',
                   tags=['nominas'])
    @action(detail=True, methods=['post'], url_path='recalculate')
    def recalculate(self, request, pk=None):
        record = self.get_object()
        if record.status in ('PAGADO', 'CANCELADO'):
            return Response({'detail': 'No se puede recalcular un recibo pagado o cancelado.'},
                            status=status.HTTP_400_BAD_REQUEST)

        from ..domain.nomina import PayrollCalculatorService
        calc   = PayrollCalculatorService()
        result = calc.calculate(
            base_salary=record.base_salary,
            extra_hours_amount=record.extra_hours_amount,
            bonuses=Decimal(str(request.data.get('bonuses', record.bonuses))),
            commissions=Decimal(str(request.data.get('commissions', record.commissions))),
            other_income=Decimal(str(request.data.get('other_income', record.other_income))),
            loans_deduction=Decimal(str(request.data.get('loans_deduction', record.loans_deduction))),
            other_deductions=Decimal(str(request.data.get('other_deductions', record.other_deductions))),
            has_infonavit=record.has_infonavit,
        )
        for field in ('bonuses', 'commissions', 'other_income', 'gross_salary',
                      'isr_deduction', 'imss_deduction', 'infonavit_deduction',
                      'loans_deduction', 'other_deductions', 'total_deductions', 'net_salary'):
            setattr(record, field, getattr(result, field))
        record.save()
        return Response(PayrollRecordSerializer(record).data)
