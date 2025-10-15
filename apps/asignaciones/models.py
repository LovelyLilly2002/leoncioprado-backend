from django.db import models, transaction
from django.utils import timezone
from apps.usuarios.models import PerfilUsuario
from apps.recursos.models import BienMaterial


class AsignacionBien(models.Model):
    ESTADOS = (
        ("ASIGNADO", "Asignado"),
        ("FINALIZADO", "Finalizado"),
        ("CANCELADO", "Cancelado"),
    )

    usuario = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name="asignaciones")
    bien = models.ForeignKey(BienMaterial, on_delete=models.CASCADE, related_name="asignaciones")
    
    fecha_asignacion = models.DateField(auto_now_add=True)
    fecha_fin = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="ASIGNADO")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Asignación {self.id} - {self.usuario.nombre} {self.usuario.apellido} ({self.estado})"

    def save(self, *args, **kwargs):
        with transaction.atomic():  # asegura que todo se guarde de manera atómica
            if self.pk is None:  # Nueva asignación
                if self.bien.cantidad_disp <= 0:
                    raise ValueError("No hay stock disponible para este bien.")
                self.bien.cantidad_disp -= 1
                self.bien.save()
            else:
                # Recupera la asignación anterior
                asignacion_antigua = AsignacionBien.objects.get(pk=self.pk)

                # Solo actuar si el estado cambia
                if asignacion_antigua.estado != self.estado:
                    # De ASIGNADO → FINALIZADO
                    if asignacion_antigua.estado == "ASIGNADO" and self.estado == "FINALIZADO":
                        self.bien.cantidad_disp += 1
                        self.fecha_fin = timezone.now().date()
                        self.bien.save()

                    # De ASIGNADO → CANCELADO
                    elif asignacion_antigua.estado == "ASIGNADO" and self.estado == "CANCELADO":
                        self.bien.cantidad_disp += 1
                        self.fecha_fin = timezone.now().date()
                        self.bien.save()

                    # Evitar cambios no válidos: FINALIZADO/CANCELADO → ASIGNADO
                    elif self.estado == "ASIGNADO":
                        raise ValueError("No se puede volver a ASIGNADO desde FINALIZADO o CANCELADO.")

            super().save(*args, **kwargs)
