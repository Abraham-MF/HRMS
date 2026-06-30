from rest_framework import serializers
import re
from ..infrastructure.models import Employee, Department, JobPosition, EmploymentHistory


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Department
        fields = ['id', 'name', 'code', 'description', 'parent', 'is_active']


class JobPositionSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model  = JobPosition
        fields = ['id', 'title', 'code', 'department', 'department_name',
                  'min_salary', 'max_salary', 'is_active']


class EmployeeListSerializer(serializers.ModelSerializer):
    # camelCase aliases
    fullName       = serializers.SerializerMethodField()
    firstName      = serializers.CharField(source='first_name', read_only=True)
    lastName       = serializers.CharField(source='last_name', read_only=True)
    employeeNumber = serializers.CharField(source='employee_number', read_only=True)
    departmentName = serializers.CharField(source='department.name', read_only=True)
    positionTitle  = serializers.CharField(source='job_position.title', read_only=True)
    employeeStatus = serializers.CharField(source='employee_status', read_only=True)
    hireDate       = serializers.DateField(source='hire_date', read_only=True)
    baseSalary     = serializers.DecimalField(source='base_salary',
                                               max_digits=12, decimal_places=2,
                                               read_only=True)
    isActive       = serializers.BooleanField(source='is_active', read_only=True)

    class Meta:
        model  = Employee
        fields = ['id', 'employeeNumber', 'firstName', 'lastName', 'fullName',
                  'email', 'departmentName', 'positionTitle', 'employeeStatus',
                  'hireDate', 'baseSalary', 'isActive']

    def get_fullName(self, obj):
        return f'{obj.first_name} {obj.last_name}'


class EmployeeDetailSerializer(serializers.ModelSerializer):
    fullName       = serializers.SerializerMethodField()
    firstName      = serializers.CharField(source='first_name')
    lastName       = serializers.CharField(source='last_name')
    employeeNumber = serializers.CharField(source='employee_number', read_only=True)
    birthDate      = serializers.DateField(source='birth_date')
    maritalStatus  = serializers.CharField(source='marital_status')
    postalCode     = serializers.CharField(source='postal_code')
    departmentId   = serializers.PrimaryKeyRelatedField(
                         source='department',
                         queryset=Department.objects.all())
    departmentName = serializers.CharField(source='department.name', read_only=True)
    jobPositionId  = serializers.PrimaryKeyRelatedField(
                         source='job_position',
                         queryset=JobPosition.objects.all())
    positionTitle  = serializers.CharField(source='job_position.title', read_only=True)
    supervisorId   = serializers.PrimaryKeyRelatedField(
                         source='supervisor', allow_null=True,
                         queryset=Employee.objects.all(), required=False)
    supervisorName = serializers.SerializerMethodField()
    hireDate       = serializers.DateField(source='hire_date')
    contractType   = serializers.CharField(source='contract_type')
    baseSalary     = serializers.DecimalField(source='base_salary',
                                               max_digits=12, decimal_places=2)
    employeeStatus = serializers.CharField(source='employee_status', read_only=True)
    isActive       = serializers.BooleanField(source='is_active', read_only=True)
    createdAt      = serializers.DateTimeField(source='created_at', read_only=True)
    age            = serializers.SerializerMethodField()

    class Meta:
        model  = Employee
        fields = [
            'id', 'employeeNumber', 'firstName', 'lastName', 'fullName',
            'curp', 'rfc', 'birthDate', 'age', 'gender', 'maritalStatus',
            'nationality', 'address', 'city', 'state', 'postalCode',
            'phone', 'email',
            'departmentId', 'departmentName', 'jobPositionId', 'positionTitle',
            'supervisorId', 'supervisorName',
            'hireDate', 'contractType', 'baseSalary', 'employeeStatus',
            'isActive', 'createdAt',
        ]
        read_only_fields = ['id', 'employeeNumber', 'employeeStatus',
                            'isActive', 'createdAt']

    def get_fullName(self, obj):
        return f'{obj.first_name} {obj.last_name}'

    def get_supervisorName(self, obj):
        if obj.supervisor:
            return f'{obj.supervisor.first_name} {obj.supervisor.last_name}'
        return None

    def get_age(self, obj):
        from datetime import date
        today = date.today()
        return today.year - obj.birth_date.year - (
            (today.month, today.day) < (obj.birth_date.month, obj.birth_date.day)
        )

    def validate_baseSalary(self, value):
        if value <= 0:
            raise serializers.ValidationError('El salario debe ser mayor a cero.')
        return value

    def validate_curp(self, value):
        if not re.match(r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$', value.upper()):
            raise serializers.ValidationError('CURP inválida.')
        return value.upper()

    def validate_rfc(self, value):
        if not re.match(r'^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$', value.upper()):
            raise serializers.ValidationError('RFC inválido.')
        return value.upper()


class EmploymentHistorySerializer(serializers.ModelSerializer):
    changeType     = serializers.CharField(source='change_type', read_only=True)
    previousValue  = serializers.CharField(source='previous_value', read_only=True)
    newValue       = serializers.CharField(source='new_value', read_only=True)
    changedAt      = serializers.DateTimeField(source='changed_at', read_only=True)

    class Meta:
        model  = EmploymentHistory
        fields = ['id', 'changeType', 'previousValue', 'newValue', 'notes', 'changedAt']