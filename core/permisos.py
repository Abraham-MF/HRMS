from rest_framework.permissions import BasePermission


class IsAdminOnly(BasePermission):
    """Solo el rol Administrador puede acceder."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role == 'ADMIN')


class IsAdminOrHR(BasePermission):
    """Administrador o Recursos Humanos."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role in ('ADMIN', 'HR'))


class IsAdminHROrSupervisor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role in ('ADMIN', 'HR', 'SUPERVISOR'))


class IsSelfOrAdminOrHR(BasePermission):
    """El empleado puede ver su propio perfil; Admin y HR pueden ver todos."""
    def has_object_permission(self, request, view, obj):
        if request.user.role in ('ADMIN', 'HR'):
            return True
        # El empleado solo puede ver su propio registro
        if hasattr(obj, 'employee'):
            return obj == request.user.employee
        return obj.id == getattr(request.user.employee, 'id', None)