from django.db import models
from django.utils import timezone
from apps.usuarios.models import PerfilUsuario
from apps.recursos.models import Bien

class AsignacionBien(models.Model):
    ESTADOS = (
        ("ASIGNADO", "Asignado"),
        ("FINALIZADO", "Finalizado"),
        ("CANCELADO", "Cancelado"),
    )

    usuario = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name="asignaciones")
    bien = models.ForeignKey(Bien, on_delete=models.CASCADE, related_name="asignaciones")
    
    fecha_asignacion = models.DateField(auto_now_add=True)
    fecha_fin = models.DateField(null=True, blank=True)  # se llena solo al finalizar
    estado = models.CharField(max_length=20, choices=ESTADOS, default="ASIGNADO")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Asignación {self.id} - {self.usuario.nombre} {self.usuario.apellido} ({self.estado})"

    def save(self, *args, **kwargs):
        """
        Manejo automático:
        - Si se crea una asignación, descuenta un bien disponible.
        - Si pasa a FINALIZADO, devuelve el bien y guarda fecha_fin.
        - Si pasa a CANCELADO, solo devuelve el bien.
        """
        if self.pk is None:  # Nueva asignación
            if self.bien.cantidad_disp > 0:
                self.bien.cantidad_disp -= 1
                self.bien.save()
        else:
            asignacion_antigua = AsignacionBien.objects.get(pk=self.pk)

            # Cuando pasa de ASIGNADO a FINALIZADO
            if asignacion_antigua.estado == "ASIGNADO" and self.estado == "FINALIZADO":
                self.bien.cantidad_disp += 1
                self.bien.save()
                self.fecha_fin = timezone.now().date()

            # Cuando pasa de ASIGNADO a CANCELADO
            if asignacion_antigua.estado == "ASIGNADO" and self.estado == "CANCELADO":
                self.bien.cantidad_disp += 1
                self.bien.save()
                self.fecha_fin = timezone.now().date()

        super().save(*args, **kwargs)
