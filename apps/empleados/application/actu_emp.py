from .datos import UpdateEmployeeDTO, EmployeeOutputDTO
from .interfaces import IEmployeeRepository


class UpdateEmployeeUseCase:
    def __init__(self, repository: IEmployeeRepository):
        self._repo = repository

    def execute(self, employee_id: str, dto: UpdateEmployeeDTO,
                changed_by: str) -> EmployeeOutputDTO:
        employee = self._repo.get_by_id(employee_id)
        if not employee:
            raise ValueError(f'Empleado {employee_id} no encontrado')

        # Aplicar solo los campos que vienen en el DTO
        for field, value in dto.__dict__.items():
            if value is not None:
                setattr(employee, field, value)

        saved = self._repo.save(employee)

        return EmployeeOutputDTO(
            id=saved.id, employee_number=saved.employee_number,
            full_name=saved.full_name, curp=saved.curp, rfc=saved.rfc,
            birth_date=saved.birth_date, age=saved.age, gender=saved.gender,
            email=saved.email, department_id=str(saved.department_id),
            job_position_id=str(saved.job_position_id), hire_date=saved.hire_date,
            contract_type=saved.contract_type, base_salary=saved.base_salary,
            employee_status=saved.employee_status, is_active=saved.is_active,
        )