import uuid
import django.db.models.deletion
import apps.documentos.infrastructure.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeDocument',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('category', models.CharField(
                    choices=[
                        ('CONTRATO', 'Contrato laboral'),
                        ('CERTIFICADO', 'Certificado'),
                        ('IDENTIFICACION', 'Identificación oficial'),
                        ('COMPROBANTE_DOMICILIO', 'Comprobante de domicilio'),
                        ('CV', 'Currículum'),
                        ('TITULO_PROFESIONAL', 'Título profesional'),
                        ('INCAPACIDAD', 'Incapacidad médica'),
                        ('OTRO', 'Otro'),
                    ],
                    default='OTRO',
                    max_length=30,
                )),
                ('title', models.CharField(max_length=200)),
                ('file', models.FileField(upload_to=apps.documentos.infrastructure.models.document_upload_path)),
                ('file_size_kb', models.PositiveIntegerField(default=0, editable=False)),
                ('mime_type', models.CharField(blank=True, editable=False, max_length=120)),
                ('notes', models.TextField(blank=True)),
                ('expires_at', models.DateField(blank=True, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('employee', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='documents',
                    to='employees.employee',
                )),
                ('uploaded_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='uploaded_documents',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'db_table': 'employee_documents',
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.AddIndex(
            model_name='employeedocument',
            index=models.Index(fields=['employee', 'is_active'], name='idx_doc_employee_active'),
        ),
        migrations.AddIndex(
            model_name='employeedocument',
            index=models.Index(fields=['category'], name='idx_doc_category'),
        ),
        migrations.AddIndex(
            model_name='employeedocument',
            index=models.Index(fields=['expires_at'], name='idx_doc_expires_at'),
        ),
    ]
