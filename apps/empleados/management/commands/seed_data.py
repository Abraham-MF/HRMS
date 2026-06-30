import random
import unicodedata
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.empleados.infrastructure.models import (
    Department, Employee, EmploymentHistory, JobPosition, WorkSchedule,
)
from apps.nominas.infrastructure.models import PayrollPeriod, PayrollRecord
from apps.asistencia.infrastructure.models import Attendance

User = get_user_model()

#datos a insertae en la db
NOMBRES_MASCULINOS = [
    "Carlos", "Miguel", "Jose", "Luis", "Juan", "Roberto", "Fernando",
    "Eduardo", "Ricardo", "Alejandro", "Daniel", "David", "Antonio",
    "Javier", "Sergio", "Marcos", "Raul", "Arturo", "Jorge", "Hector",
]

NOMBRES_FEMENINOS = [
    "Maria", "Ana", "Laura", "Sofia", "Gabriela", "Patricia", "Claudia",
    "Veronica", "Sandra", "Adriana", "Valeria", "Fernanda", "Alejandra",
    "Monica", "Beatriz", "Liliana", "Diana", "Carolina", "Elena", "Rosa",
]

APELLIDOS = [
    "Garcia", "Martinez", "Lopez", "Gonzalez", "Hernandez", "Perez",
    "Sanchez", "Ramirez", "Torres", "Flores", "Rivera", "Gomez",
    "Diaz", "Reyes", "Cruz", "Morales", "Gutierrez", "Ortiz",
    "Jimenez", "Mendoza", "Castillo", "Alvarez", "Moreno", "Vargas",
    "Romero", "Herrera", "Medina", "Aguilar", "Vazquez", "Rojas",
]

DEPARTAMENTOS = [
    {"name": "Recursos Humanos", "code": "RH"},
    {"name": "Tecnologia",       "code": "TI"},
    {"name": "Finanzas",         "code": "FIN"},
    {"name": "Ventas",           "code": "VEN"},
    {"name": "Operaciones",      "code": "OPS"},
]

PUESTOS = [
    {"title": "Director de RH",         "code": "DIR-RH",   "dept": "RH",  "min": 45000, "max": 70000},
    {"title": "Analista de RH",         "code": "ANA-RH",   "dept": "RH",  "min": 15000, "max": 25000},
    {"title": "Gerente de TI",          "code": "GER-TI",   "dept": "TI",  "min": 40000, "max": 65000},
    {"title": "Desarrollador Backend",  "code": "DEV-BE",   "dept": "TI",  "min": 20000, "max": 40000},
    {"title": "Desarrollador Frontend", "code": "DEV-FE",   "dept": "TI",  "min": 18000, "max": 35000},
    {"title": "Contador Senior",        "code": "CONT-SR",  "dept": "FIN", "min": 22000, "max": 38000},
    {"title": "Auxiliar Contable",      "code": "AUX-CONT", "dept": "FIN", "min": 10000, "max": 18000},
    {"title": "Ejecutivo de Ventas",    "code": "EJE-VEN",  "dept": "VEN", "min": 12000, "max": 22000},
    {"title": "Supervisor de Ventas",   "code": "SUP-VEN",  "dept": "VEN", "min": 20000, "max": 32000},
    {"title": "Coordinador Operativo",  "code": "CORD-OPS", "dept": "OPS", "min": 16000, "max": 28000},
]

HORARIOS = [
    {"name": "Turno Matutino",   "mon_s": "08:00", "mon_e": "17:00", "fri_s": "08:00", "fri_e": "17:00", "hours": 40},
    {"name": "Turno Vespertino", "mon_s": "14:00", "mon_e": "22:00", "fri_s": "14:00", "fri_e": "22:00", "hours": 40},
    {"name": "Medio Tiempo",     "mon_s": "09:00", "mon_e": "13:00", "fri_s": "09:00", "fri_e": "13:00", "hours": 20},
    {"name": "Flexible",         "mon_s": "09:00", "mon_e": "18:00", "fri_s": "09:00", "fri_e": "15:00", "hours": 40},
]

ESTADOS_MX = [
    "Ciudad de Mexico", "Jalisco", "Nuevo Leon", "Puebla", "Guanajuato",
    "Veracruz", "Estado de Mexico", "Chihuahua", "Sonora", "Coahuila",
]

ESTADOS_CIVILES = ["Soltero", "Casado", "Divorciado", "Viudo", "Union libre"]

# Helpers
def to_ascii(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def gen_curp(nombre: str, apellido: str, sexo: str, nacimiento: date, idx: int) -> str:
    """CURP sintética (no válida fiscalmente)."""
    n = (apellido[:2] + nombre[0] + str(nacimiento.year)[-2:] +
         f"{nacimiento.month:02d}{nacimiento.day:02d}" +
         ("H" if sexo == "MASCULINO" else "M") +
         "CMX" + apellido[1].upper() + nombre[1].upper() +
         f"{idx:02d}")
    return n[:18].upper()


def gen_rfc(apellido: str, nombre: str, nacimiento: date, idx: int) -> str:
    base = (apellido[:2] + nombre[0] + str(nacimiento.year)[-2:] +
            f"{nacimiento.month:02d}{nacimiento.day:02d}")
    sufijo = f"{idx:03d}"
    return (base + sufijo)[:13].upper()


def calc_isr(bruto: Decimal) -> Decimal:
    if bruto <= Decimal("7142.90"):
        return (bruto * Decimal("0.0192")).quantize(Decimal("0.01"))
    elif bruto <= Decimal("12211.96"):
        return (Decimal("137.03") + (bruto - Decimal("7142.90")) * Decimal("0.064")).quantize(Decimal("0.01"))
    elif bruto <= Decimal("21363.95"):
        return (Decimal("461.40") + (bruto - Decimal("12211.96")) * Decimal("0.1088")).quantize(Decimal("0.01"))
    elif bruto <= Decimal("24852.20"):
        return (Decimal("1457.87") + (bruto - Decimal("21363.95")) * Decimal("0.16")).quantize(Decimal("0.01"))
    else:
        return (Decimal("2015.87") + (bruto - Decimal("24852.20")) * Decimal("0.1792")).quantize(Decimal("0.01"))


def calc_imss(bruto: Decimal) -> Decimal:
    return (bruto * Decimal("0.0225")).quantize(Decimal("0.01"))

# Command
class Command(BaseCommand):
    help = "Genera 100 usuarios/empleados de prueba con nomina y asistencia"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Elimina todos los datos existentes antes de insertar",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write(self.style.WARNING("Eliminando datos existentes..."))
            Attendance.objects.all().delete()
            PayrollRecord.objects.all().delete()
            PayrollPeriod.objects.all().delete()
            EmploymentHistory.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            User.objects.filter(is_superuser=True).delete()
            Employee.objects.all().delete()
            JobPosition.objects.all().delete()
            Department.objects.all().delete()
            WorkSchedule.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("   Datos eliminados."))

        #Horarios
        self.stdout.write("Creando horarios...")
        from django.utils.dateparse import parse_time
        schedules = {}
        for h in HORARIOS:
            ws, _ = WorkSchedule.objects.get_or_create(
                name=h["name"],
                defaults={
                    "monday_start": parse_time(h["mon_s"]),
                    "monday_end":   parse_time(h["mon_e"]),
                    "friday_start": parse_time(h["fri_s"]),
                    "friday_end":   parse_time(h["fri_e"]),
                    "weekly_hours": h["hours"],
                },
            )
            schedules[h["name"]] = ws

        #Departamentos
        self.stdout.write("Creando departamentos...")
        depts = {}
        for d in DEPARTAMENTOS:
            dept, _ = Department.objects.get_or_create(
                code=d["code"],
                defaults={"name": d["name"]},
            )
            depts[d["code"]] = dept

        #Puestos
        self.stdout.write("Creando puestos...")
        positions = {}
        for p in PUESTOS:
            pos, _ = JobPosition.objects.get_or_create(
                code=p["code"],
                defaults={
                    "title":      p["title"],
                    "department": depts[p["dept"]],
                    "min_salary": Decimal(str(p["min"])),
                    "max_salary": Decimal(str(p["max"])),
                },
            )
            positions[p["code"]] = pos

        #Empleados y Usuarios
        self.stdout.write("Creando 100 empleados y usuarios...")

        role_plan = (
            [("ADMIN", "DIR-RH")] +
            [("HR",    "ANA-RH")] * 3 +
            [("SUPERVISOR", "SUP-VEN")] * 6 +
            [("EMPLOYEE", None)] * 90
        )
        random.shuffle(role_plan[1:])

        position_codes_by_dept = {
            "RH":  ["DIR-RH", "ANA-RH"],
            "TI":  ["GER-TI", "DEV-BE", "DEV-FE"],
            "FIN": ["CONT-SR", "AUX-CONT"],
            "VEN": ["EJE-VEN", "SUP-VEN"],
            "OPS": ["CORD-OPS"],
        }
        dept_codes    = list(depts.keys())
        schedule_list = list(schedules.values())

        today      = date.today()
        hire_start = date(2018, 1, 1)
        employees_created = []

        for i, (role, forced_pos) in enumerate(role_plan):
            gender = random.choice(["MASCULINO", "FEMENINO"])
            nombre   = random.choice(NOMBRES_MASCULINOS if gender == "MASCULINO" else NOMBRES_FEMENINOS)
            apellido1 = random.choice(APELLIDOS)
            apellido2 = random.choice(APELLIDOS)
            full_last = f"{apellido1} {apellido2}"
            nacimiento = random_date(date(1970, 1, 1), date(2000, 12, 31))

            # CURP y RFC únicos por índice
            curp = gen_curp(nombre, apellido1, gender, nacimiento, i)
            rfc  = gen_rfc(apellido1, nombre, nacimiento, i)

            nombre_ascii   = to_ascii(nombre).lower()
            apellido_ascii = to_ascii(apellido1).lower()
            email = f"{nombre_ascii}.{apellido_ascii}{i}@andevia.com"

            emp_num = f"EMP{str(i + 1).zfill(4)}"

            #Puesto y departamento
            dept_code = random.choice(dept_codes)
            if forced_pos:
                pos_code = forced_pos
                for d_code, p_codes in position_codes_by_dept.items():
                    if forced_pos in p_codes:
                        dept_code = d_code
                        break
            else:
                pos_code = random.choice(position_codes_by_dept[dept_code])

            position = positions[pos_code]
            dept     = depts[dept_code]
            schedule = random.choice(schedule_list)

            min_s  = float(position.min_salary or 10000)
            max_s  = float(position.max_salary or 30000)
            salary = Decimal(str(round(random.uniform(min_s, max_s), 2)))
            hire_date = random_date(hire_start, today - timedelta(days=30))
            contract  = random.choice(["INDEFINIDO", "INDEFINIDO", "DETERMINADO", "HONORARIOS"])
            estado    = random.choice(ESTADOS_MX)

            emp = Employee.objects.create(
                employee_number=emp_num,
                first_name=nombre,
                last_name=full_last,
                curp=curp,
                rfc=rfc,
                birth_date=nacimiento,
                gender=gender,
                marital_status=random.choice(ESTADOS_CIVILES),
                nationality="Mexicana",
                address=f"Calle {random.randint(1,200)} #{random.randint(1,500)}",
                city=estado,
                state=estado,
                postal_code=str(random.randint(10000, 99999)),
                phone=f"55{random.randint(10000000, 99999999)}",
                email=email,
                department=dept,
                job_position=position,
                schedule=schedule,
                hire_date=hire_date,
                contract_type=contract,
                base_salary=salary,
                employee_status="ACTIVO",
                is_active=True,
            )
            employees_created.append((emp, role))

        self.stdout.write(f"   {len(employees_created)} empleados creados")

        #Usuarios
        self.stdout.write("Creando usuarios...")
        users_created = 0
        for emp, role in employees_created:
            fn_ascii  = to_ascii(emp.first_name).lower()
            ln_ascii  = to_ascii(emp.last_name.split()[0]).lower()
            username  = f"{fn_ascii}.{ln_ascii}{emp.employee_number[-3:]}"[:60]

            u = User.objects.create_user(
                email=emp.email,
                username=username,
                password="Test12345",
                role=role,
                is_staff=(role in ("ADMIN", "HR")),
                employee=emp,
            )
            if role == "ADMIN":
                u.is_superuser = True
                u.save()
            users_created += 1

        self.stdout.write(f"   {users_created} usuarios creados")

        #Período de nómina
        self.stdout.write("Creando nomina...")
        import calendar
        if today.day >= 16:
            period_start = date(today.year, today.month, 1)
            period_end   = date(today.year, today.month, 15)
        else:
            prev_month = today.month - 1 if today.month > 1 else 12
            prev_year  = today.year if today.month > 1 else today.year - 1
            last_day   = calendar.monthrange(prev_year, prev_month)[1]
            period_start = date(prev_year, prev_month, 16)
            period_end   = date(prev_year, prev_month, last_day)

        period, _ = PayrollPeriod.objects.get_or_create(
            start_date=period_start,
            end_date=period_end,
            defaults={
                "period_type": "QUINCENAL",
                "status":      "CERRADO",
                "closed_at":   timezone.now(),
            },
        )

        payroll_records = []
        for emp, _ in employees_created:
            base      = emp.base_salary / 2
            extra_hrs = Decimal(str(round(random.uniform(0, 20), 2)))
            hourly    = emp.base_salary / Decimal("160")
            extra_amt = (extra_hrs * hourly * Decimal("2")).quantize(Decimal("0.01"))
            bonuses   = Decimal(str(round(random.uniform(0, 2000), 2))) if random.random() < 0.3 else Decimal("0")
            gross     = (base + extra_amt + bonuses).quantize(Decimal("0.01"))
            isr       = calc_isr(gross)
            imss      = calc_imss(gross)
            infonavit = (gross * Decimal("0.05")).quantize(Decimal("0.01")) if random.random() < 0.6 else Decimal("0")
            total_ded = (isr + imss + infonavit).quantize(Decimal("0.01"))
            net       = (gross - total_ded).quantize(Decimal("0.01"))

            payroll_records.append(PayrollRecord(
                employee=emp,
                period=period,
                base_salary=base,
                extra_hours_amount=extra_amt,
                bonuses=bonuses,
                commissions=Decimal("0"),
                other_income=Decimal("0"),
                gross_salary=gross,
                isr_deduction=isr,
                imss_deduction=imss,
                infonavit_deduction=infonavit,
                loans_deduction=Decimal("0"),
                other_deductions=Decimal("0"),
                total_deductions=total_ded,
                net_salary=net,
                status="PAGADO",
            ))

        PayrollRecord.objects.bulk_create(payroll_records, ignore_conflicts=True)
        self.stdout.write(f"   {len(payroll_records)} registros de nomina creados")

        #Asistencia
        self.stdout.write("Creando asistencia (30 dias habiles)...")
        work_days = []
        d = today - timedelta(days=50)
        while d <= today and len(work_days) < 30:
            if d.weekday() < 5:
                work_days.append(d)
            d += timedelta(days=1)

        attendance_records = []
        for emp, _ in employees_created:
            for work_date in work_days:
                is_absence = random.random() < 0.05
                if is_absence:
                    attendance_records.append(Attendance(
                        employee=emp,
                        work_date=work_date,
                        is_absence=True,
                        hours_worked=Decimal("0"),
                        extra_hours=Decimal("0"),
                        late_minutes=0,
                        notes="Ausencia" if random.random() < 0.5 else "",
                    ))
                else:
                    late_min    = random.randint(0, 30) if random.random() < 0.15 else 0
                    check_in_dt = timezone.make_aware(
                        datetime(work_date.year, work_date.month, work_date.day, 8, 0)
                        + timedelta(minutes=late_min)
                    )
                    hours_total = round(random.uniform(7.5, 10), 2)
                    check_out_dt = check_in_dt + timedelta(hours=hours_total)
                    extra = max(Decimal("0"), Decimal(str(round(hours_total - 8, 2))))

                    attendance_records.append(Attendance(
                        employee=emp,
                        work_date=work_date,
                        check_in=check_in_dt,
                        check_out=check_out_dt,
                        hours_worked=Decimal(str(round(hours_total, 2))),
                        extra_hours=extra,
                        late_minutes=late_min,
                        is_absence=False,
                    ))

        Attendance.objects.bulk_create(attendance_records, ignore_conflicts=True)
        self.stdout.write(f"   {len(attendance_records)} registros de asistencia creados")

        #Resumen
        admin_user = User.objects.filter(role="ADMIN").first()
        hr_user    = User.objects.filter(role="HR").first()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 55))
        self.stdout.write(self.style.SUCCESS("SEED COMPLETADO"))
        self.stdout.write(self.style.SUCCESS("=" * 55))
        self.stdout.write(f"  Empleados   : {Employee.objects.count()}")
        self.stdout.write(f"  Usuarios    : {User.objects.count()}")
        self.stdout.write(f"  Nominas     : {PayrollRecord.objects.count()}")
        self.stdout.write(f"  Asistencias : {Attendance.objects.count()}")
        self.stdout.write("")
        self.stdout.write("  ROLES:")
        self.stdout.write(f"    ADMIN      : {User.objects.filter(role='ADMIN').count()}")
        self.stdout.write(f"    HR         : {User.objects.filter(role='HR').count()}")
        self.stdout.write(f"    SUPERVISOR : {User.objects.filter(role='SUPERVISOR').count()}")
        self.stdout.write(f"    EMPLOYEE   : {User.objects.filter(role='EMPLOYEE').count()}")
        self.stdout.write("")
        self.stdout.write("  CREDENCIALES:")
        if admin_user:
            self.stdout.write(self.style.WARNING(f"    Admin → {admin_user.email}"))
        if hr_user:
            self.stdout.write(self.style.WARNING(f"    HR    → {hr_user.email}"))
        self.stdout.write(self.style.WARNING("    Password de todos: Test12345"))
        self.stdout.write(self.style.SUCCESS("=" * 55))
