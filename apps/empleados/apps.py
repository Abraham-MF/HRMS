from django.apps import AppConfig


class EmpleadosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.empleados"
    label = "employees"  # matches FK string 'employees.Employee' in auth model
    
    def ready(self):
        import apps.empleados.infrastructure.cambios  # noqa: signals
