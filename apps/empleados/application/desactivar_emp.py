from .interfaces import IEmployeeRepository
from django.utils import timezone


class DeactivateEmployeeUseCase:
    def __init__(self, repository: IEmployeeRepository):
        self._repo = repository

    def execute(self, employee_id: str) -> None:
        employee = self._repo.get_by_id(employee_id)
        if not employee:
            raise ValueError(f'Empleado {employee_id} no encontrado')
        if not employee.is_active:
            raise ValueError('El empleado ya se encuentra dado de baja')

        employee.deactivate()
        self._repo.save(employee)