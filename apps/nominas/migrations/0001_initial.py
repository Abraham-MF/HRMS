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
            name='PayrollPeriod',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('period_type', models.CharField(choices=[('SEMANAL', 'Semanal'), ('QUINCENAL', 'Quincenal'), ('MENSUAL', 'Mensual')], default='QUINCENAL', max_length=15)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('status', models.CharField(choices=[('ABIERTO', 'Abierto'), ('CERRADO', 'Cerrado'), ('PAGADO', 'Pagado')], default='ABIERTO', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={'db_table': 'payroll_periods', 'ordering': ['-start_date']},
        ),
        migrations.CreateModel(
            name='PayrollRecord',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('base_salary', models.DecimalField(decimal_places=2, max_digits=12)),
                ('extra_hours_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('bonuses', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('commissions', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('other_income', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('gross_salary', models.DecimalField(decimal_places=2, max_digits=12)),
                ('isr_deduction', models.DecimalField(decimal_places=2, max_digits=10)),
                ('imss_deduction', models.DecimalField(decimal_places=2, max_digits=10)),
                ('infonavit_deduction', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('loans_deduction', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('other_deductions', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_deductions', models.DecimalField(decimal_places=2, max_digits=12)),
                ('net_salary', models.DecimalField(decimal_places=2, max_digits=12)),
                ('status', models.CharField(choices=[('CALCULADO', 'Calculado'), ('APROBADO', 'Aprobado'), ('PAGADO', 'Pagado'), ('CANCELADO', 'Cancelado')], default='CALCULADO', max_length=15)),
                ('bank_name', models.CharField(blank=True, max_length=100)),
                ('account_number', models.CharField(blank=True, max_length=30)),
                ('clabe', models.CharField(blank=True, max_length=18)),
                ('transaction_id', models.CharField(blank=True, max_length=100)),
                ('has_infonavit', models.BooleanField(default=False)),
                ('extra_hours', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('calculated_at', models.DateTimeField(auto_now_add=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('calculated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='calculated_payrolls', to='authentication.user')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payroll_records', to='employees.employee')),
                ('period', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='records', to='nominas.payrollperiod')),
            ],
            options={'db_table': 'payroll_records', 'ordering': ['-calculated_at']},
        ),
        migrations.AlterUniqueTogether(
            name='payrollrecord',
            unique_together={('employee', 'period')},
        ),
    ]
