from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0001_initial'),
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('work_date', models.DateField()),
                ('check_in', models.DateTimeField(blank=True, null=True)),
                ('check_out', models.DateTimeField(blank=True, null=True)),
                ('hours_worked', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('extra_hours', models.DecimalField(decimal_places=2, default=0, max_digits=4)),
                ('late_minutes', models.PositiveIntegerField(default=0)),
                ('is_absence', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='employees.employee')),
            ],
            options={'db_table': 'attendance'},
        ),
        migrations.CreateModel(
            name='LeaveBalance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('year', models.PositiveSmallIntegerField()),
                ('entitled_days', models.DecimalField(decimal_places=1, max_digits=5)),
                ('used_days', models.DecimalField(decimal_places=1, default=0, max_digits=5)),
                ('pending_days', models.DecimalField(decimal_places=1, default=0, max_digits=5)),
                ('remaining_days', models.DecimalField(decimal_places=1, max_digits=5)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leave_balance', to='employees.employee')),
            ],
            options={'db_table': 'leave_balance'},
        ),
        migrations.CreateModel(
            name='LeaveRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('leave_type', models.CharField(choices=[('VACACIONES', 'Vacaciones'), ('PERSONAL', 'Permiso personal'), ('MEDICO', 'Permiso médico'), ('DUELO', 'Duelo'), ('OTRO', 'Otro')], max_length=20)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('total_days', models.PositiveSmallIntegerField()),
                ('reason', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('APROBADA', 'Aprobada'), ('RECHAZADA', 'Rechazada'), ('CANCELADA', 'Cancelada')], default='PENDIENTE', max_length=20)),
                ('review_notes', models.TextField(blank=True)),
                ('requested_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leave_requests', to='employees.employee')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_leaves', to='employees.employee')),
            ],
            options={'db_table': 'leave_requests'},
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('license_type', models.CharField(choices=[('INCAPACIDAD', 'Incapacidad médica'), ('MATERNIDAD', 'Licencia de maternidad'), ('PATERNIDAD', 'Licencia de paternidad'), ('PERMISO_ESPECIAL', 'Permiso especial'), ('PERMISO_SIN_GOCE', 'Permiso sin goce de sueldo')], max_length=25)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('total_days', models.PositiveSmallIntegerField()),
                ('with_pay', models.BooleanField(default=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='licenses', to='employees.employee')),
                ('registered_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='authentication.user')),
            ],
            options={'db_table': 'licenses'},
        ),
        migrations.AlterIndexTogether(
            name='attendance',
            index_together={('employee', 'work_date')},
        ),
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together={('employee', 'work_date')},
        ),
        migrations.AlterUniqueTogether(
            name='leavebalance',
            unique_together={('employee', 'year')},
        ),
    ]
