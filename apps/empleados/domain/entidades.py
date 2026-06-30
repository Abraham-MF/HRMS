from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional
import uuid


@dataclass
class Employee:
    """Entidad de dominio pura — sin dependencias de Django."""
    id:               str
    employee_number:  str
    first_name:       str
    last_name:        str
    curp:             str
    rfc:              str
    birth_date:       date
    gender:           str
    email:            str
    department_id:    str
    job_position_id:  str
    hire_date:        date
    contract_type:    str
    base_salary:      Decimal
    employee_status:  str           = 'ACTIVO'
    marital_status:   Optional[str] = None
    nationality:      str           = 'Mexicana'
    address:          Optional[str] = None
    city:             Optional[str] = None
    state:            Optional[str] = None
    postal_code:      Optional[str] = None
    phone:            Optional[str] = None
    supervisor_id:    Optional[str] = None
    schedule_id:      Optional[str] = None
    is_active:        bool          = True

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    @property
    def age(self) -> int:
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    def deactivate(self) -> None:
        """Baja lógica del empleado."""
        self.is_active       = False
        self.employee_status = 'BAJA'

    def update_salary(self, new_salary: Decimal) -> None:
        if new_salary <= 0:
            raise ValueError('El salario debe ser mayor a cero')
        self.base_salary = new_salary