from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Employee, EmploymentHistory


@receiver(pre_save, sender=Employee)
def track_employment_changes(sender, instance, **kwargs):
    """
    Detecta cambios en campos críticos antes de guardar
    y registra el historial automáticamente.
    """
    if not instance.pk:
        return  # nuevo registro, no hay historial previo

    try:
        previous = Employee.objects.get(pk=instance.pk)
    except Employee.DoesNotExist:
        return

    TRACKED_FIELDS = {
        'base_salary':     EmploymentHistory.ChangeType.SALARY_CHANGE,
        'department':      EmploymentHistory.ChangeType.DEPARTMENT_CHANGE,
        'job_position':    EmploymentHistory.ChangeType.POSITION_CHANGE,
        'employee_status': EmploymentHistory.ChangeType.STATUS_CHANGE,
    }

    records = []
    for field, change_type in TRACKED_FIELDS.items():
        prev_val = getattr(previous, field + '_id' if field in
                           ('department', 'job_position') else field)
        new_val  = getattr(instance, field + '_id' if field in
                           ('department', 'job_position') else field)

        if str(prev_val) != str(new_val):
            records.append(EmploymentHistory(
                employee=instance,
                change_type=change_type,
                previous_value=str(prev_val),
                new_value=str(new_val),
            ))

    if records:
        EmploymentHistory.objects.bulk_create(records)