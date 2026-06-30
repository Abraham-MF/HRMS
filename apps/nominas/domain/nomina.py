from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass


@dataclass
class PayrollResult:
    base_salary:          Decimal
    extra_hours_amount:   Decimal
    bonuses:              Decimal
    commissions:          Decimal
    other_income:         Decimal
    gross_salary:         Decimal
    isr_deduction:        Decimal
    imss_deduction:       Decimal
    infonavit_deduction:  Decimal
    loans_deduction:      Decimal
    other_deductions:     Decimal
    total_deductions:     Decimal
    net_salary:           Decimal


class PayrollCalculatorService:
    """
    Motor de cálculo de nómina.
    Aplica tablas ISR 2024 (SAT México), cuotas IMSS e INFONAVIT.
    Principio OCP: agregar nuevas deducciones = nueva clase, no modificar esta.
    """

    # Tabla ISR mensual 2024 — SAT México
    ISR_TABLE = [
        # (límite_inferior, límite_superior, cuota_fija, porcentaje_excedente)
        (Decimal('0.01'),       Decimal('746.04'),    Decimal('0.00'),    Decimal('1.92')),
        (Decimal('746.05'),     Decimal('6332.05'),   Decimal('14.32'),   Decimal('6.40')),
        (Decimal('6332.06'),    Decimal('11128.01'),  Decimal('371.83'),  Decimal('10.88')),
        (Decimal('11128.02'),   Decimal('12935.82'),  Decimal('893.63'),  Decimal('16.00')),
        (Decimal('12935.83'),   Decimal('15487.71'),  Decimal('1182.88'), Decimal('17.92')),
        (Decimal('15487.72'),   Decimal('31236.49'),  Decimal('1640.18'), Decimal('21.36')),
        (Decimal('31236.50'),   Decimal('49233.00'),  Decimal('5004.12'), Decimal('23.52')),
        (Decimal('49233.01'),   Decimal('93993.90'),  Decimal('9236.89'), Decimal('30.00')),
        (Decimal('93993.91'),   Decimal('125325.20'), Decimal('22665.17'),Decimal('32.00')),
        (Decimal('125325.21'),  Decimal('375975.61'), Decimal('32691.18'),Decimal('34.00')),
        (Decimal('375975.62'),  Decimal('9999999.99'),Decimal('117912.32'),Decimal('35.00')),
    ]

    # Porcentajes IMSS cuota obrera 2024
    IMSS_ENFERMEDAD_MATERNIDAD = Decimal('0.4')     # 0.40%
    IMSS_INVALIDEZ_VIDA        = Decimal('0.625')   # 0.625%
    IMSS_CESANTIA_VEJEZ        = Decimal('1.125')   # 1.125%
    IMSS_TOTAL_PERCENT         = (IMSS_ENFERMEDAD_MATERNIDAD +
                                   IMSS_INVALIDEZ_VIDA +
                                   IMSS_CESANTIA_VEJEZ)  # 2.15%

    # INFONAVIT cuota obrera
    INFONAVIT_PERCENT = Decimal('1.0')   # 1% del SBC

    # Salario mínimo diario 2024 (zona general)
    SALARIO_MINIMO_DIARIO = Decimal('248.93')

    def calculate(
        self,
        base_salary:         Decimal,
        extra_hours_amount:  Decimal = Decimal('0'),
        bonuses:             Decimal = Decimal('0'),
        commissions:         Decimal = Decimal('0'),
        other_income:        Decimal = Decimal('0'),
        loans_deduction:     Decimal = Decimal('0'),
        other_deductions:    Decimal = Decimal('0'),
        has_infonavit:       bool    = False,
    ) -> PayrollResult:
        # ── 1. Ingresos totales ────────────────────────────────────────
        gross_salary = (
            base_salary + extra_hours_amount +
            bonuses + commissions + other_income
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # ── 2. ISR ────────────────────────────────────────────────────
        isr = self._calculate_isr(gross_salary)

        # ── 3. IMSS cuota obrera ──────────────────────────────────────
        sbc_diario = (base_salary / Decimal('30')).quantize(Decimal('0.01'))
        imss = (sbc_diario * 30 * self.IMSS_TOTAL_PERCENT / 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

        # ── 4. INFONAVIT ──────────────────────────────────────────────
        infonavit = Decimal('0')
        if has_infonavit:
            infonavit = (sbc_diario * 30 * self.INFONAVIT_PERCENT / 100).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

        # ── 5. Totales ────────────────────────────────────────────────
        total_deductions = (isr + imss + infonavit +
                            loans_deduction + other_deductions).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        net_salary = (gross_salary - total_deductions).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

        if net_salary < Decimal('0'):
            raise ValueError('El salario neto no puede ser negativo. Revise las deducciones.')

        return PayrollResult(
            base_salary=base_salary,
            extra_hours_amount=extra_hours_amount,
            bonuses=bonuses,
            commissions=commissions,
            other_income=other_income,
            gross_salary=gross_salary,
            isr_deduction=isr,
            imss_deduction=imss,
            infonavit_deduction=infonavit,
            loans_deduction=loans_deduction,
            other_deductions=other_deductions,
            total_deductions=total_deductions,
            net_salary=net_salary,
        )

    def _calculate_isr(self, gross: Decimal) -> Decimal:
        """Aplica tabla ISR mensual SAT 2024."""
        for li, ls, cuota, porcentaje in self.ISR_TABLE:
            if li <= gross <= ls:
                excedente = gross - li + Decimal('0.01')
                isr = cuota + (excedente * porcentaje / 100)
                return isr.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        # Si supera el último rango (no debería ocurrir con la tabla completa)
        _, _, cuota, porcentaje = self.ISR_TABLE[-1]
        li = self.ISR_TABLE[-1][0]
        excedente = gross - li
        return (cuota + excedente * porcentaje / 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

    def calculate_extra_hours(self, hourly_rate: Decimal,
                               extra_hours: Decimal) -> Decimal:
        """
        LFT Art. 67: primeras 9 horas extra/semana al doble.
        Horas adicionales al triple.
        """
        double_hours = min(extra_hours, Decimal('9'))
        triple_hours = max(extra_hours - Decimal('9'), Decimal('0'))
        return (
            (double_hours * hourly_rate * 2) +
            (triple_hours * hourly_rate * 3)
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)