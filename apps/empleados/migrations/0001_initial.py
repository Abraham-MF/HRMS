import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        # NO dependency on authentication here — breaks the cycle.
        # EmploymentHistory.changed_by uses swappable_dependency instead.
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='children',
                    to='employees.department',
                )),
            ],
            options={'db_table': 'departments', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='WorkSchedule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('monday_start', models.TimeField(blank=True, null=True)),
                ('monday_end', models.TimeField(blank=True, null=True)),
                ('friday_start', models.TimeField(blank=True, null=True)),
                ('friday_end', models.TimeField(blank=True, null=True)),
                ('weekly_hours', models.PositiveSmallIntegerField(default=40)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'db_table': 'work_schedules'},
        ),
        migrations.CreateModel(
            name='JobPosition',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=150)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('description', models.TextField(blank=True)),
                ('min_salary', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('max_salary', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('department', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='positions',
                    to='employees.department',
                )),
            ],
            options={'db_table': 'job_positions'},
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('employee_number', models.CharField(max_length=20, unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('curp', models.CharField(max_length=18, unique=True)),
                ('rfc', models.CharField(max_length=13, unique=True)),
                ('birth_date', models.DateField()),
                ('gender', models.CharField(
                    choices=[
                        ('MASCULINO', 'Masculino'),
                        ('FEMENINO', 'Femenino'),
                        ('NO_BINARIO', 'No binario'),
                    ],
                    max_length=20,
                )),
                ('marital_status', models.CharField(blank=True, max_length=20)),
                ('nationality', models.CharField(default='Mexicana', max_length=60)),
                ('address', models.CharField(blank=True, max_length=255)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('state', models.CharField(blank=True, max_length=100)),
                ('postal_code', models.CharField(blank=True, max_length=5)),
                ('phone', models.CharField(blank=True, max_length=15)),
                ('email', models.EmailField(unique=True)),
                ('hire_date', models.DateField()),
                ('contract_type', models.CharField(
                    choices=[
                        ('INDEFINIDO', 'Contrato indefinido'),
                        ('DETERMINADO', 'Contrato por tiempo determinado'),
                        ('HONORARIOS', 'Honorarios profesionales'),
                    ],
                    max_length=20,
                )),
                ('base_salary', models.DecimalField(decimal_places=2, max_digits=12)),
                ('employee_status', models.CharField(
                    choices=[
                        ('ACTIVO', 'Activo'),
                        ('BAJA', 'Baja'),
                        ('SUSPENDIDO', 'Suspendido'),
                        ('VACACIONES', 'En vacaciones'),
                    ],
                    default='ACTIVO',
                    max_length=20,
                )),
                ('is_active', models.BooleanField(default=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('department', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='employees',
                    to='employees.department',
                )),
                ('job_position', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='employees',
                    to='employees.jobposition',
                )),
                ('schedule', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='employees.workschedule',
                )),
                ('supervisor', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='subordinates',
                    to='employees.employee',
                )),
            ],
            options={
                'db_table': 'employees',
                'ordering': ['last_name', 'first_name'],
                'indexes': [
                    models.Index(fields=['department', 'is_active'], name='idx_emp_dept_active'),
                    models.Index(fields=['employee_status'], name='idx_emp_status'),
                    models.Index(fields=['supervisor'], name='idx_emp_supervisor'),
                ],
            },
        ),
        migrations.AddField(
            model_name='department',
            name='manager',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='managed_departments',
                to='employees.employee',
            ),
        ),
        migrations.CreateModel(
            name='EmploymentHistory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('change_type', models.CharField(
                    choices=[
                        ('SALARY_CHANGE', 'Cambio salarial'),
                        ('DEPARTMENT_CHANGE', 'Cambio de departamento'),
                        ('POSITION_CHANGE', 'Cambio de cargo'),
                        ('PROMOTION', 'Ascenso'),
                        ('TRANSFER', 'Transferencia'),
                        ('REHIRE', 'Reingreso'),
                        ('STATUS_CHANGE', 'Cambio de estatus'),
                    ],
                    max_length=30,
                )),
                ('previous_value', models.CharField(blank=True, max_length=255)),
                ('new_value', models.CharField(blank=True, max_length=255)),
                ('notes', models.TextField(blank=True)),
                ('changed_at', models.DateTimeField(auto_now_add=True)),
                ('employee', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='employment_history',
                    to='employees.employee',
                )),
                ('changed_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'db_table': 'employment_history', 'ordering': ['-changed_at']},
        ),
    ]
