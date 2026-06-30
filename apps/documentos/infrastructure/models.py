import uuid
from django.conf import settings
from django.db import models


def document_upload_path(instance, filename):
    """
    Organiza los archivos por empleado dentro del bucket/almacenamiento:
    documents/<employee_id>/<uuid>_<filename original>
    """
    ext = filename.rsplit('.', 1)[-1] if '.' in filename else ''
    safe_name = uuid.uuid4().hex
    new_name = f'{safe_name}.{ext}' if ext else safe_name
    return f'documents/{instance.employee_id}/{new_name}'


class EmployeeDocument(models.Model):
    """
    Almacenamiento de documentos importantes del personal:
    contratos, certificados, identificaciones, comprobantes, etc.

    El archivo en sí se guarda en el storage configurado por Django
    (FileSystemStorage en desarrollo, S3/MinIO en producción —
    ver config/settings/desarrollo.py y config/settings/principal.py).
    Solo se conservan en este modelo la ruta/metadatos del archivo.
    """

    class Category(models.TextChoices):
        CONTRACT          = 'CONTRATO',              'Contrato laboral'
        CERTIFICATE       = 'CERTIFICADO',            'Certificado'
        ID_DOCUMENT        = 'IDENTIFICACION',        'Identificación oficial'
        PROOF_OF_ADDRESS  = 'COMPROBANTE_DOMICILIO',  'Comprobante de domicilio'
        RESUME            = 'CV',                     'Currículum'
        DEGREE            = 'TITULO_PROFESIONAL',     'Título profesional'
        MEDICAL_LEAVE     = 'INCAPACIDAD',             'Incapacidad médica'
        OTHER             = 'OTRO',                    'Otro'

    ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx']
    MAX_FILE_SIZE_MB   = 10

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee     = models.ForeignKey(
                       'employees.Employee', on_delete=models.CASCADE,
                       related_name='documents')
    category     = models.CharField(max_length=30, choices=Category.choices,
                       default=Category.OTHER)
    title        = models.CharField(max_length=200)
    file         = models.FileField(upload_to=document_upload_path)
    file_size_kb = models.PositiveIntegerField(editable=False, default=0)
    mime_type    = models.CharField(max_length=120, blank=True, editable=False)
    notes        = models.TextField(blank=True)
    expires_at   = models.DateField(null=True, blank=True)
    uploaded_by  = models.ForeignKey(
                       settings.AUTH_USER_MODEL, null=True, blank=True,
                       on_delete=models.SET_NULL, related_name='uploaded_documents')
    uploaded_at  = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    is_active    = models.BooleanField(default=True)
    deleted_at   = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'employee_documents'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['employee', 'is_active'], name='idx_doc_employee_active'),
            models.Index(fields=['category'],               name='idx_doc_category'),
            models.Index(fields=['expires_at'],              name='idx_doc_expires_at'),
        ]

    def __str__(self):
        return f'{self.title} — {self.employee.full_name}'

    @property
    def file_name(self) -> str:
        return self.file.name.rsplit('/', 1)[-1] if self.file else ''
