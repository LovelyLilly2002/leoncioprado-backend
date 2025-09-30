from django.db import models
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
        if self.pk:  # Ya existe → revisar si el estado cambió
            prestamo_anterior = Prestamo.objects.get(pk=self.pk)
            if prestamo_anterior.estado != self.estado:
                if self.estado == "ACTIVO" and self.recurso.cantidad > 0:
                    self.recurso.cantidad -= 1
                    self.recurso.save()
                elif self.estado == "FINALIZADO" and prestamo_anterior.estado == "ACTIVO":
                    self.recurso.cantidad += 1
                    self.recurso.save()
        else:
            # Nuevo préstamo
            if self.estado == "ACTIVO" and self.recurso.cantidad > 0:
                self.recurso.cantidad -= 1
                self.recurso.save()

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
        if self.pk:  # Ya existe → revisar cambio de estado
            reserva_anterior = Reserva.objects.get(pk=self.pk)
            if reserva_anterior.estado != self.estado:
                if self.estado == "ACEPTADA" and self.recurso.cantidad > 0:
                    self.recurso.cantidad -= 1
                    self.recurso.save()
                elif self.estado == "RECHAZADA" and reserva_anterior.estado == "ACEPTADA":
                    # Si estaba aceptada y se rechaza → se devuelve stock
                    self.recurso.cantidad += 1
                    self.recurso.save()
        else:
            # Nueva reserva aceptada directamente
            if self.estado == "ACEPTADA" and self.recurso.cantidad > 0:
                self.recurso.cantidad -= 1
                self.recurso.save()

        super().save(*args, **kwargs)

