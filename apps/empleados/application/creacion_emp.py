import uuid
from decimal import Decimal
from .datos import CreateEmployeeDTO, EmployeeOutputDTO
from .interfaces import IEmployeeRepository
from ..domain.entidades import Employee
from ..domain.value_objects import CURP, RFC, Money


class CreateEmployeeUseCase:
    """
    Caso de uso: registrar un nuevo empleado.
    Principio SRP: solo sabe crear empleados.
    Principio DIP: depende de la abstracción IEmployeeRepository.
    """

    def __init__(self, repository: IEmployeeRepository):
        self._repo = repository

    def execute(self, dto: CreateEmployeeDTO) -> EmployeeOutputDTO:
        # Validaciones de dominio
        CURP(dto.curp)   # lanza ValueError si inválida
        RFC(dto.rfc)     # lanza ValueError si inválida
        Money(dto.base_salary)

        # Unicidad de CURP y RFC
        if self._repo.exists_curp(dto.curp):
            raise ValueError(f'Ya existe un empleado con CURP {dto.curp}')
        if self._repo.exists_rfc(dto.rfc):
            raise ValueError(f'Ya existe un empleado con RFC {dto.rfc}')

        # Construir entidad de dominio
        employee = Employee(
            id=str(uuid.uuid4()),
            **dto.__dict__
        )

        # Persistir
        saved = self._repo.save(employee)

        return self._to_output(saved)

    def _to_output(self, e: Employee) -> EmployeeOutputDTO:
        return EmployeeOutputDTO(
            id=e.id, employee_number=e.employee_number,
            full_name=e.full_name, curp=e.curp, rfc=e.rfc,
            birth_date=e.birth_date, age=e.age, gender=e.gender,
            email=e.email, department_id=e.department_id,
            job_position_id=e.job_position_id, hire_date=e.hire_date,
            contract_type=e.contract_type, base_salary=e.base_salary,
            employee_status=e.employee_status, is_active=e.is_active,
        )
    
    