from django.db import models
from django.utils import timezone
from apps.usuarios.models import PerfilUsuario
from apps.recursos.models import Recurso


class Prestamo(models.Model):
    ESTADOS = (
        ('PENDIENTE', 'Pendiente'),
        ('ACTIVO', 'Activo'),
        ('FINALIZADO', 'Finalizado'),
    )

    usuario = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name="prestamos")
    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE, related_name="prestamos")
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=15, choices=ESTADOS, default="PENDIENTE")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Préstamo {self.id} - {self.usuario.nombre} {self.usuario.apellido} ({self.estado})"

    def save(self, *args, **kwargs):
        # Si se activa un préstamo → restar stock
        if self.estado == "ACTIVO" and self.recurso.cantidad > 0:
            self.recurso.cantidad = max(0, self.recurso.cantidad - 1)
            self.recurso.save()

        # Si finaliza → devolver stock
        if self.estado == "FINALIZADO":
            self.recurso.cantidad += 1
            self.recurso.save()
            # Guardar fecha de devolución automáticamente
            if not self.fecha_devolucion:
                self.fecha_devolucion = timezone.now()

        super().save(*args, **kwargs)


class Reserva(models.Model):
    ESTADOS = (
        ('PENDIENTE', 'Pendiente'),
        ('ACEPTADA', 'Aceptada'),
        ('RECHAZADA', 'Rechazada'),
    )

    usuario = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name="reservas")
    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE, related_name="reservas")
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=15, choices=ESTADOS, default="PENDIENTE")
    prioridad = models.PositiveIntegerField(default=1)  # Cola de espera (1 = más urgente)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reserva {self.id} - {self.usuario.nombre} {self.usuario.apellido} ({self.estado})"

    def save(self, *args, **kwargs):
        # Si la reserva se acepta → crear un préstamo
        if self.estado == "ACEPTADA":
            if self.recurso.cantidad > 0:  # Solo si hay stock
                prestamo = Prestamo.objects.create(
                    usuario=self.usuario,
                    recurso=self.recurso,
                    estado="ACTIVO",
                    fecha_entrega=timezone.now()
                )
                prestamo.save()
            else:
                # No hay stock, se deja en pendiente
                self.estado = "PENDIENTE"

        super().save(*args, **kwargs)


