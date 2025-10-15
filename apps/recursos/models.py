from django.db import models

# Create your models here.
class Recurso(models.Model):
    TIPOS = (
        ('LIBRO', 'Libro'),
        ('BIEN', 'Bien'),
        ('OTROS', 'Otros'),
    )

    codigo_barra = models.CharField(max_length=50, blank=True, null=True) 
    cantidad = models.PositiveIntegerField(default=1)  
    tipo = models.CharField(max_length=20, choices=TIPOS)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tipo} - {self.codigo_barra if self.codigo_barra else 'Sin código'}"


class Libro(models.Model):
    recurso = models.OneToOneField(Recurso, on_delete=models.CASCADE, primary_key=True)
    titulo = models.CharField(max_length=100)
    autor = models.CharField(max_length=100, blank=True)
    editorial = models.CharField(max_length=100, blank=True) 
    anio = models.PositiveIntegerField(null=True, blank=True)
    descripcion = models.TextField(blank=True)
    cantidad_total = models.PositiveIntegerField(default=1)
    cantidad_disp = models.PositiveIntegerField(default=1)

    @property
    def esta_disponible(self):
        return self.cantidad_disp > 0

    def __str__(self):
        estado = "Disponible" if self.esta_disponible else "No disponible"
        return f"{self.titulo} ({estado})"

class BienMaterial(models.Model):
    TIPO_BIEN = (
        ('MOVIL', 'Móvil'),
        ('INMOVIL', 'Inmóvil'),
    )
    ESTADO_BIEN = (
        ('DISPONIBLE', 'Disponible'),
        ('REPARACION', 'En reparación'),
        ('BAJA', 'Baja'),
    )

    recurso = models.OneToOneField(Recurso, on_delete=models.CASCADE, primary_key=True)
    nombre = models.CharField(max_length=100)
    tipo_bien = models.CharField(max_length=10, choices=TIPO_BIEN)
    serie = models.CharField(max_length=50, blank=True, null=True, unique=True)  
    estado = models.CharField(max_length=15, choices=ESTADO_BIEN, default='DISPONIBLE')
    descripcion = models.TextField(blank=True)
    cantidad_total = models.PositiveIntegerField(default=1)
    cantidad_disp = models.PositiveIntegerField(default=1)

    @property
    def esta_disponible(self):
         """Devuelve True si hay stock y el bien está en estado DISPONIBLE."""
         return self.cantidad_disp > 0 and self.estado == 'DISPONIBLE'

    def __str__(self):
        disponibilidad = "Disponible" if self.esta_disponible else "No disponible"
        return f"{self.nombre} ({disponibilidad})"

