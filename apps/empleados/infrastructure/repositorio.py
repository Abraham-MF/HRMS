# apps/employees/infrastructure/repositories.py
from typing import List, Optional, Tuple
from django.db.models import Q
from django.utils import timezone
from ..application.interfaces import IEmployeeRepository
from ..domain.entidades import Employee as EmployeeDomain
from .models import Employee as EmployeeModel


class DjangoEmployeeRepository(IEmployeeRepository):
    """Implementación concreta del repositorio usando Django ORM."""

    def get_by_id(self, employee_id: str) -> Optional[EmployeeDomain]:
        try:
            obj = EmployeeModel.objects.select_related(
                'department', 'job_position', 'supervisor', 'schedule'
            ).get(id=employee_id, is_active=True)
            return self._to_domain(obj)
        except EmployeeModel.DoesNotExist:
            return None

    def get_all(self, filters: dict = None,
                page: int = 1, page_size: int = 20
                ) -> Tuple[List[EmployeeDomain], int]:
        qs = EmployeeModel.objects.select_related(
            'department', 'job_position'
        ).filter(is_active=True)

        if filters:
            if search := filters.get('search'):
                qs = qs.filter(
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search)  |
                    Q(employee_number__icontains=search)
                )
            if dept := filters.get('department_id'):
                qs = qs.filter(department_id=dept)
            if status := filters.get('employee_status'):
                qs = qs.filter(employee_status=status)
            if position := filters.get('job_position_id'):
                qs = qs.filter(job_position_id=position)

        total = qs.count()
        offset = (page - 1) * page_size
        objs = qs[offset: offset + page_size]
        return [self._to_domain(o) for o in objs], total

    def save(self, employee: EmployeeDomain) -> EmployeeDomain:
        obj, _ = EmployeeModel.objects.update_or_create(
            id=employee.id,
            defaults={
                'employee_number': employee.employee_number,
                'first_name':      employee.first_name,
                'last_name':       employee.last_name,
                'curp':            employee.curp,
                'rfc':             employee.rfc,
                'birth_date':      employee.birth_date,
                'gender':          employee.gender,
                'marital_status':  employee.marital_status or '',
                'nationality':     employee.nationality,
                'address':         employee.address or '',
                'city':            employee.city or '',
                'state':           employee.state or '',
                'postal_code':     employee.postal_code or '',
                'phone':           employee.phone or '',
                'email':           employee.email,
                'department_id':   employee.department_id,
                'job_position_id': employee.job_position_id,
                'supervisor_id':   employee.supervisor_id,
                'schedule_id':     employee.schedule_id,
                'hire_date':       employee.hire_date,
                'contract_type':   employee.contract_type,
                'base_salary':     employee.base_salary,
                'employee_status': employee.employee_status,
                'is_active':       employee.is_active,
                'deleted_at':      None if employee.is_active else timezone.now(),
            }
        )
        return self._to_domain(obj)

    def delete(self, employee_id: str) -> None:
        EmployeeModel.objects.filter(id=employee_id).update(
            is_active=False, employee_status='BAJA', deleted_at=timezone.now()
        )

    def exists_curp(self, curp: str, exclude_id: str = None) -> bool:
        qs = EmployeeModel.objects.filter(curp=curp.upper())
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        return qs.exists()

    def exists_rfc(self, rfc: str, exclude_id: str = None) -> bool:
        qs = EmployeeModel.objects.filter(rfc=rfc.upper())
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        return qs.exists()

    def _to_domain(self, obj: EmployeeModel) -> EmployeeDomain:
        return EmployeeDomain(
            id=str(obj.id),
            employee_number=obj.employee_number,
            first_name=obj.first_name,
            last_name=obj.last_name,
            curp=obj.curp,
            rfc=obj.rfc,
            birth_date=obj.birth_date,
            gender=obj.gender,
            marital_status=obj.marital_status or None,
            nationality=obj.nationality,
            address=obj.address or None,
            city=obj.city or None,
            state=obj.state or None,
            postal_code=obj.postal_code or None,
            phone=obj.phone or None,
            email=obj.email,
            department_id=str(obj.department_id),
            job_position_id=str(obj.job_position_id),
            supervisor_id=str(obj.supervisor_id) if obj.supervisor_id else None,
            schedule_id=str(obj.schedule_id) if obj.schedule_id else None,
            hire_date=obj.hire_date,
            contract_type=obj.contract_type,
            base_salary=obj.base_salary,
            employee_status=obj.employee_status,
            is_active=obj.is_active,
        )