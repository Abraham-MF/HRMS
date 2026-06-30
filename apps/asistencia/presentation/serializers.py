from rest_framework import serializers
from django.utils import timezone
from ..infrastructure.models import Attendance, LeaveRequest, LeaveBalance, License


class AttendanceSerializer(serializers.ModelSerializer):
    employeeName = serializers.CharField(source='employee.full_name', read_only=True)
    workDate     = serializers.DateField(source='work_date')
    checkIn      = serializers.DateTimeField(source='check_in', allow_null=True, required=False)
    checkOut     = serializers.DateTimeField(source='check_out', allow_null=True, required=False)
    hoursWorked  = serializers.DecimalField(source='hours_worked', max_digits=5,
                                             decimal_places=2, allow_null=True, read_only=True)
    extraHours   = serializers.DecimalField(source='extra_hours', max_digits=5,
                                             decimal_places=2, read_only=True)
    lateMinutes  = serializers.IntegerField(source='late_minutes', read_only=True)
    isAbsence    = serializers.BooleanField(source='is_absence', required=False)

    class Meta:
        model  = Attendance
        fields = ['id', 'employee', 'employeeName', 'workDate',
                  'checkIn', 'checkOut', 'hoursWorked', 'extraHours',
                  'lateMinutes', 'isAbsence', 'notes']
        read_only_fields = ['id', 'employeeName', 'hoursWorked', 'extraHours', 'lateMinutes']


class CheckInSerializer(serializers.Serializer):
    employee_id = serializers.UUIDField()
    notes       = serializers.CharField(required=False, allow_blank=True)


class CheckOutSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)


class LeaveRequestSerializer(serializers.ModelSerializer):
    employeeName  = serializers.CharField(source='employee.full_name', read_only=True)
    reviewedName  = serializers.SerializerMethodField()
    leaveType     = serializers.CharField(source='leave_type')
    startDate     = serializers.DateField(source='start_date')
    endDate       = serializers.DateField(source='end_date')
    totalDays     = serializers.IntegerField(source='total_days')
    reviewNotes   = serializers.CharField(source='review_notes', allow_blank=True, required=False)
    requestedAt   = serializers.DateTimeField(source='requested_at', read_only=True)
    reviewedAt    = serializers.DateTimeField(source='reviewed_at', read_only=True, allow_null=True)
    durationDays  = serializers.SerializerMethodField()

    class Meta:
        model  = LeaveRequest
        fields = ['id', 'employee', 'employeeName', 'leaveType',
                  'startDate', 'endDate', 'totalDays', 'reason',
                  'status', 'reviewed_by', 'reviewedName',
                  'reviewNotes', 'requestedAt', 'reviewedAt', 'durationDays']
        read_only_fields = ['id', 'employeeName', 'reviewedName', 'status',
                            'reviewed_by', 'reviewNotes', 'requestedAt',
                            'reviewedAt', 'durationDays']

    def get_reviewedName(self, obj):
        if obj.reviewed_by:
            return obj.reviewed_by.full_name
        return None

    def get_durationDays(self, obj):
        return (obj.end_date - obj.start_date).days + 1

    def validate(self, data):
        start = data.get('start_date')
        end   = data.get('end_date')
        if start and end and start > end:
            raise serializers.ValidationError('La fecha de inicio debe ser anterior a la de fin.')
        return data


class LeaveApprovalSerializer(serializers.Serializer):
    action       = serializers.ChoiceField(choices=['approve', 'reject'])
    review_notes = serializers.CharField(required=False, allow_blank=True)


class LeaveBalanceSerializer(serializers.ModelSerializer):
    employeeName  = serializers.CharField(source='employee.full_name', read_only=True)
    entitledDays  = serializers.IntegerField(source='entitled_days', read_only=True)
    usedDays      = serializers.IntegerField(source='used_days', read_only=True)
    pendingDays   = serializers.IntegerField(source='pending_days', read_only=True)
    remainingDays = serializers.IntegerField(source='remaining_days', read_only=True)

    class Meta:
        model  = LeaveBalance
        fields = ['id', 'employee', 'employeeName', 'year',
                  'entitledDays', 'usedDays', 'pendingDays', 'remainingDays']
        read_only_fields = fields


class LicenseSerializer(serializers.ModelSerializer):
    employeeName = serializers.CharField(source='employee.full_name', read_only=True)
    licenseType  = serializers.CharField(source='license_type')
    startDate    = serializers.DateField(source='start_date')
    endDate      = serializers.DateField(source='end_date')
    totalDays    = serializers.IntegerField(source='total_days', read_only=True)
    withPay      = serializers.BooleanField(source='with_pay')

    class Meta:
        model  = License
        fields = ['id', 'employee', 'employeeName', 'licenseType',
                  'startDate', 'endDate', 'totalDays', 'withPay', 'notes']
        read_only_fields = ['id', 'employeeName', 'totalDays']