import re
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CURP:
    value: str

    def __post_init__(self):
        pattern = r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$'
        if not re.match(pattern, self.value.upper()):
            raise ValueError(f'CURP inválida: {self.value}')

    def __str__(self):
        return self.value.upper()


@dataclass(frozen=True)
class RFC:
    value: str

    def __post_init__(self):
        pattern = r'^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$'
        if not re.match(pattern, self.value.upper()):
            raise ValueError(f'RFC inválido: {self.value}')

    def __str__(self):
        return self.value.upper()


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = 'MXN'

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError('El monto monetario no puede ser negativo')

    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError('No se pueden sumar montos en diferente moneda')
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: 'Money') -> 'Money':
        result = self.amount - other.amount
        if result < 0:
            raise ValueError('El resultado no puede ser negativo')
        return Money(result, self.currency)

    def __str__(self):
        return f'${self.amount:,.2f} {self.currency}'