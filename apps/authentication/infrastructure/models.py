import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)   # bcrypt automático via Django
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields['is_staff']     = True
        extra_fields['is_superuser'] = True
        extra_fields['role']         = User.Role.ADMIN
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN      = 'ADMIN',      'Administrador'
        HR         = 'HR',         'Recursos Humanos'
        SUPERVISOR = 'SUPERVISOR', 'Supervisor'
        EMPLOYEE   = 'EMPLOYEE',   'Empleado'

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email       = models.EmailField(unique=True)
    username    = models.CharField(max_length=60, unique=True)
    role        = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    employee    = models.OneToOneField(
        'employees.Employee', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='user_account'
    )
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    last_login  = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    objects  = UserManager()
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def __str__(self):
        return f'{self.email} ({self.get_role_display()})'

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_hr(self):
        return self.role in (self.Role.ADMIN, self.Role.HR)