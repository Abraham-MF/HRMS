import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Adds the FK from User to Employee.
    Must run AFTER both authentication.0001 and employees.0001 exist,
    which is guaranteed by the dependencies below.
    """

    dependencies = [
        ('authentication', '0001_initial'),
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='employee',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='user_account',
                to='employees.employee',
            ),
        ),
    ]
