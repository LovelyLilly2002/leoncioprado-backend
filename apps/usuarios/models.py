# apps/usuarios/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class Cuenta(AbstractUser):
    """
    Modelo de Usuario Personalizado que extiende AbstractUser de Django.
    Utiliza el campo 'email' como único y añade un campo 'rol'.
    """
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('RESP_BIBLIOTECA', 'Responsable de Biblioteca'),
        ('RESP_BIENES', 'Responsable de Bienes'),
        ('GENERAL', 'Usuario General'),
    )

    email = models.EmailField(unique=True, verbose_name="Correo Electrónico")
    rol = models.CharField(max_length=20, choices=ROLES, default='GENERAL')
    is_active = models.BooleanField(default=True, verbose_name="Está Activo")

    # Campos de AbstractUser: username, first_name, last_name, is_staff, is_superuser, last_login, date_joined, password

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cuenta de Usuario"
        verbose_name_plural = "Cuentas de Usuarios"

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
    
    # Asegurarse de que el email se use como el USERNAME_FIELD
    # Ya que AbstractUser utiliza 'username' por defecto. Si quieres usar email para el login,
    # deberías definir USERNAME_FIELD = 'email' y cambiar el username a null=True, blank=True
    # pero como no lo has hecho, mantendremos el 'username' por defecto y forzamos el email a ser único.


class Turno(models.Model):
    """Modelo para definir el turno (Mañana, Tarde, Noche)."""
    nombre = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name_plural = "Turnos"

    def __str__(self):
        return self.nombre


class Nivel(models.Model):
    """Modelo para definir el nivel (Inicial, Primaria, Secundaria)."""
    nombre = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name_plural = "Niveles"

    def __str__(self):
        return self.nombre


class Grado(models.Model):
    """
    Modelo para definir un grado/aula específico, por ejemplo:
    '1°' 'A' - 'Primaria' ('Mañana')
    """
    # *CORRECCIÓN/OPTIMIZACIÓN*: Se eliminó null=True, blank=True para forzar que
    # un Grado siempre pertenezca a un Nivel y un Turno, garantizando la integridad.
    nivel = models.ForeignKey(
        'Nivel', 
        on_delete=models.CASCADE, 
        related_name='grados', 
        verbose_name="Nivel Educativo"
    )
    nombre = models.CharField(max_length=50, verbose_name="Grado (e.g., 1°, 2°)")
    seccion = models.CharField(max_length=10, verbose_name="Sección (e.g., A, B)")
    turno = models.ForeignKey(
        'Turno', 
        on_delete=models.CASCADE, 
        related_name='grados'
    )

    class Meta:
        verbose_name_plural = "Grados"
        # La unicidad es crucial: no pueden existir dos 'Grados' idénticos en la misma
        # 'Sección', 'Nivel' y 'Turno'.
        unique_together = ('nombre', 'seccion', 'nivel', 'turno')

    def __str__(self):
        # La representación es más limpia y clara
        return f"{self.nombre} {self.seccion} - {self.nivel.nombre} ({self.turno.nombre})"


class PerfilUsuario(models.Model):
    """
    Modelo para almacenar información adicional de un usuario (Cuenta) que no es de autenticación.
    Relación 1 a 1 con Cuenta.
    """
    cuenta = models.OneToOneField(
        Cuenta, 
        on_delete=models.CASCADE,
        primary_key=True # Usar el ID de Cuenta como PK del Perfil (opcional, pero limpio)
    )
    dni = models.CharField(max_length=15, unique=True, verbose_name="DNI/Identificación")
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20, blank=True, null=True) # El teléfono puede no ser obligatorio
    # Un perfil puede no tener un grado (e.g., si es ADMIN o RESPONSABLE)
    grado = models.ForeignKey(
        Grado, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Grado/Aula Asignado"
    )

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.cuenta.username}"