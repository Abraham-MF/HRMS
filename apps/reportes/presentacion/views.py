from datetime import date, timedelta
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.empleados.infrastructure.models import Employee, Department
from apps.asistencia.infrastructure.models import Attendance, LeaveRequest
from apps.nominas.infrastructure.models import PayrollRecord
from core.permisos import IsAdminOrHR


class DashboardView(APIView):
    permission_classes = [IsAdminOrHR]

    def get(self, request):
        today = date.today()
        first_of_month = today.replace(day=1)

        #Empleados
        employees_qs      = Employee.objects.filter(is_active=True)
        total_employees   = Employee.objects.count()
        active_employees  = employees_qs.filter(employee_status='ACTIVO').count()
        new_this_month    = employees_qs.filter(hire_date__gte=first_of_month).count()

        #Asistencia de hoy
        on_leave_today = LeaveRequest.objects.filter(
            status='APROBADO',
            start_date__lte=today,
            end_date__gte=today,
        ).count()

        absences_today = Attendance.objects.filter(
            work_date=today,
            is_absence=True,
        ).count()

        #Nómina del mes
        payroll_this_month = PayrollRecord.objects.filter(
            period__start_date__gte=first_of_month,
        ).aggregate(
            total=Sum('gross_salary'),
            avg=Avg('base_salary'),
        )
        total_payroll_month = float(payroll_this_month['total'] or 0)
        avg_salary          = float(payroll_this_month['avg'] or
                                    employees_qs.aggregate(a=Avg('base_salary'))['a'] or 0)

        #Headcount por departamento
        headcount_by_dept = list(
            employees_qs
            .filter(employee_status='ACTIVO')
            .values('department__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:6]
        )
        headcount_by_dept = [
            {'name': d['department__name'] or 'Sin depto', 'count': d['count']}
            for d in headcount_by_dept
        ]

        #Asistencia últimos 7 días
        attendance_last_7 = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            present = Attendance.objects.filter(work_date=day, is_absence=False).count()
            absent  = Attendance.objects.filter(work_date=day, is_absence=True).count()
            attendance_last_7.append({
                'date':    day.strftime('%d/%m'),
                'present': present,
                'absent':  absent,
            })

        #Nómina últimos 6 meses
        payroll_last_6 = []
        for i in range(5, -1, -1):
            #primer día del mes correspondiente
            month_start = (today.replace(day=1) - timedelta(days=i * 28)).replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1)

            total = PayrollRecord.objects.filter(
                period__start_date__gte=month_start,
                period__start_date__lt=month_end,
            ).aggregate(t=Sum('gross_salary'))['t'] or 0

            payroll_last_6.append({
                'month': month_start.strftime('%b %Y'),
                'total': float(total),
            })

        return Response({
            'totalEmployees':      total_employees,
            'activeEmployees':     active_employees,
            'newThisMonth':        new_this_month,
            'onLeaveToday':        on_leave_today,
            'absencesToday':       absences_today,
            'totalPayrollMonth':   total_payroll_month,
            'avgSalary':           avg_salary,
            'headcountByDept':     headcount_by_dept,
            'attendanceLast7Days': attendance_last_7,
            'payrollLast6Months':  payroll_last_6,
        })