from django.db import models

# Create your models here.
class Recurso(models.Model):
    TIPO_RECURSO = (
        ('LIBRO', 'Libro'),
        ('BIEN', 'Bien'),
        ('OTROS', 'Otros'),
    )
    tipo = models.CharField(max_length=20, choices=TIPO_RECURSO)
    codigo_barra = models.CharField(max_length=50, blank=True, null=True) 
    cantidad = models.PositiveIntegerField(default=1)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Libro(models.Model):
    id_recurso = models.OneToOneField('Recurso', on_delete=models.CASCADE, primary_key=True)
    titulo = models.CharField(max_length=100)
    autor = models.CharField(max_length=100, blank=True)
    editorial = models.CharField(max_length=50, blank=True)
    anio = models.IntegerField(null=True, blank=True)
    descripcion = models.TextField(blank=True)
    cantidad_total = models.PositiveIntegerField(default=1)
    cantidad_disp = models.PositiveIntegerField(default=1)

    @property
    def esta_disponible(self):
        return self.cantidad_disp > 0

    def __str__(self):
        return f"{self.titulo} ({'Disponible' if self.esta_disponible else 'No disponible'})"

class Bien(models.Model):
    TIPO_BIEN = (
        ('MOVIL', 'Móvil'),
        ('INMOVIL', 'Inmóvil'),
    )
    ESTADO_BIEN = (
        ('DISPONIBLE', 'Disponible'),
        ('REPARACION', 'En reparación'),
        ('BAJA', 'Baja'),
    )

    id_recurso = models.OneToOneField('Recurso', on_delete=models.CASCADE, primary_key=True)
    nombre = models.CharField(max_length=100)
    tipo_bien = models.CharField(max_length=10, choices=TIPO_BIEN)
    serie = models.CharField(max_length=50, blank=True, null=True)  
    estado = models.CharField(max_length=15, choices=ESTADO_BIEN, default='DISPONIBLE')
    descripcion = models.TextField(blank=True)
    cantidad_total = models.PositiveIntegerField(default=1)
    cantidad_disp = models.PositiveIntegerField(default=1)

    @property
    def esta_disponible(self):
        """Devuelve True si hay unidades disponibles y el estado es DISPONIBLE"""
        return self.cantidad_disp > 0 and self.estado == 'DISPONIBLE'

    def __str__(self):
        disponibilidad = 'Disponible' if self.esta_disponible else 'No disponible'
        return f"{self.nombre} ({disponibilidad})"

