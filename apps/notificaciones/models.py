from django.db import models
from apps.usuarios.models import PerfilUsuario


class Notificacion(models.Model):
    TIPOS = (
        ('PRESTAMO', 'Préstamo'),
        ('RESERVA', 'Reserva'),
        ('GENERAL', 'General'),
    )

    usuario = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name="notificaciones")
    tipo = models.CharField(max_length=20, choices=TIPOS, default="GENERAL")
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)  # Para marcar si el usuario ya la vio
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        estado = "Leída" if self.leida else "No leída"
        return f"Notificación {self.id} - {self.usuario.nombre} {self.usuario.apellido} ({estado})"
