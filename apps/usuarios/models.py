from django.db import models
from django.contrib.auth.models import AbstractUser
#Ya tienes username, password y otros campos en AbstractUser.
# Create your models here.
class Cuenta(AbstractUser):
    ROLES = (
        ('ADMIN', 'Admin'),
        ('RESP_BIBLIOTECA', 'Responsable de Biblioteca'),
        ('RESP_BIENES', 'Responsable de Bienes'),
        ('GENERAL', 'Usuario General'),
    )

    rol = models.CharField(max_length=20, choices=ROLES, default='GENERAL')
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.rol})"


class Turno(models.Model):
    nombre = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nombre


class Grado(models.Model):
    nombre = models.CharField(max_length=50)      
    nivel = models.CharField(max_length=20)  
    seccion = models.CharField(max_length=10)            
    turnos = models.ManyToManyField(Turno, blank=True)  # selección múltiple

    def __str__(self):
        return f"{self.nombre} {self.seccion}"



class PerfilUsuario(models.Model):
    cuenta = models.OneToOneField(Cuenta, on_delete=models.CASCADE)
    dni = models.CharField(max_length=15, unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    grado = models.ForeignKey(Grado, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.cuenta.rol}"

    