from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass
class CreateEmployeeDTO:
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
    marital_status:   Optional[str] = None
    nationality:      str           = 'Mexicana'
    address:          Optional[str] = None
    city:             Optional[str] = None
    state:            Optional[str] = None
    postal_code:      Optional[str] = None
    phone:            Optional[str] = None
    supervisor_id:    Optional[str] = None
    schedule_id:      Optional[str] = None


@dataclass
class UpdateEmployeeDTO:
    first_name:      Optional[str]     = None
    last_name:       Optional[str]     = None
    email:           Optional[str]     = None
    phone:           Optional[str]     = None
    address:         Optional[str]     = None
    city:            Optional[str]     = None
    state:           Optional[str]     = None
    postal_code:     Optional[str]     = None
    department_id:   Optional[str]     = None
    job_position_id: Optional[str]     = None
    base_salary:     Optional[Decimal] = None
    supervisor_id:   Optional[str]     = None
    employee_status: Optional[str]     = None
    marital_status:  Optional[str]     = None


@dataclass
class EmployeeOutputDTO:
    id:              str
    employee_number: str
    full_name:       str
    curp:            str
    rfc:             str
    birth_date:      date
    age:             int
    gender:          str
    email:           str
    department_id:   str
    job_position_id: str
    hire_date:       date
    contract_type:   str
    base_salary:     Decimal
    employee_status: str
    is_active:       bool