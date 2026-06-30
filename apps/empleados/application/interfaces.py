from abc import ABC, abstractmethod
from typing import List, Optional
from ..domain.entidades import Employee


class IEmployeeRepository(ABC):
    """Contrato que debe cumplir cualquier implementación de repositorio."""

    @abstractmethod
    def get_by_id(self, employee_id: str) -> Optional[Employee]: ...

    @abstractmethod
    def get_all(self, filters: dict = None, page: int = 1,
                page_size: int = 20) -> tuple[List[Employee], int]: ...

    @abstractmethod
    def save(self, employee: Employee) -> Employee: ...

    @abstractmethod
    def delete(self, employee_id: str) -> None: ...

    @abstractmethod
    def exists_curp(self, curp: str, exclude_id: str = None) -> bool: ...

    @abstractmethod
    def exists_rfc(self, rfc: str, exclude_id: str = None) -> bool: ...