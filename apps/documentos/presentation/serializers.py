from rest_framework import serializers
from ..infrastructure.models import EmployeeDocument
from apps.empleados.infrastructure.models import Employee


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer para lectura y escritura de documentos del personal.
    Expone los campos en camelCase para que coincidan con el contrato
    que ya consume el frontend (módulo documentos).
    """
    employeeId    = serializers.PrimaryKeyRelatedField(
                        source='employee', queryset=Employee.objects.all())
    employeeName  = serializers.SerializerMethodField()
    fileName      = serializers.SerializerMethodField()
    fileSizeKB    = serializers.IntegerField(source='file_size_kb', read_only=True)
    mimeType      = serializers.CharField(source='mime_type', read_only=True)
    uploadedAt    = serializers.DateTimeField(source='uploaded_at', read_only=True)
    uploadedBy    = serializers.SerializerMethodField()
    expiresAt     = serializers.DateField(source='expires_at', required=False,
                        allow_null=True)
    url           = serializers.SerializerMethodField()

    class Meta:
        model  = EmployeeDocument
        fields = [
            'id', 'employeeId', 'employeeName', 'category', 'title',
            'file', 'fileName', 'fileSizeKB', 'mimeType',
            'uploadedAt', 'uploadedBy', 'expiresAt', 'notes', 'url',
        ]
        extra_kwargs = {
            'file': {'write_only': True},
        }

    def get_employeeName(self, obj):
        return obj.employee.full_name

    def get_fileName(self, obj):
        return obj.file_name

    def get_uploadedBy(self, obj):
        return obj.uploaded_by.username if obj.uploaded_by else None

    def get_url(self, obj):
        request = self.context.get('request')
        if not obj.file:
            return None
        url = obj.file.url
        return request.build_absolute_uri(url) if request else url

    def validate_file(self, value):
        ext = value.name.rsplit('.', 1)[-1].lower() if '.' in value.name else ''
        if ext not in EmployeeDocument.ALLOWED_EXTENSIONS:
            allowed = ', '.join(EmployeeDocument.ALLOWED_EXTENSIONS)
            raise serializers.ValidationError(
                f'Tipo de archivo no permitido. Formatos válidos: {allowed}.')

        max_bytes = EmployeeDocument.MAX_FILE_SIZE_MB * 1024 * 1024
        if value.size > max_bytes:
            raise serializers.ValidationError(
                f'El archivo supera el límite de {EmployeeDocument.MAX_FILE_SIZE_MB} MB.')

        return value

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('El título es obligatorio.')
        return value.strip()

    def create(self, validated_data):
        file_obj = validated_data.get('file')
        validated_data['file_size_kb'] = max(1, round(file_obj.size / 1024))
        validated_data['mime_type']    = getattr(file_obj, 'content_type', '') or ''

        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data['uploaded_by'] = request.user

        return super().create(validated_data)
