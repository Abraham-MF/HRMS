from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class PaymentRequest:
    employee_id:    str
    employee_name:  str
    amount:         Decimal
    bank_name:      str
    account_number: str
    clabe:          str
    reference:      str
    period:         str


@dataclass
class PaymentResponse:
    success:       bool
    reference:     str
    status:        str
    message:       str
    transaction_id: str = None


class IBankingGateway(ABC):
    """
    Interfaz que desacopla el sistema de pagos del proveedor bancario.
    Principio OCP: agregar BBVA, SPEI, STP = nueva clase, no modificar las existentes.
    """

    @abstractmethod
    def send_payment(self, request: PaymentRequest) -> PaymentResponse: ...

    @abstractmethod
    def get_payment_status(self, transaction_id: str) -> PaymentResponse: ...


#Implementación mock para desarrollo
import uuid
import random

class MockBankingGateway(IBankingGateway):
    """Simula integración bancaria. Reemplazar en producción por STPGateway."""

    def send_payment(self, request: PaymentRequest) -> PaymentResponse:
        # Simula latencia de red
        success = random.random() > 0.05  # 95% de éxito
        txn_id  = str(uuid.uuid4())
        return PaymentResponse(
            success=success,
            reference=request.reference,
            status='COMPLETADO' if success else 'RECHAZADO',
            message='Transferencia exitosa' if success else 'Error bancario simulado',
            transaction_id=txn_id if success else None,
        )

    def get_payment_status(self, transaction_id: str) -> PaymentResponse:
        return PaymentResponse(
            success=True,
            reference=transaction_id,
            status='COMPLETADO',
            message='Pago confirmado',
            transaction_id=transaction_id,
        )