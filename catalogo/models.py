from django.conf import settings
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=60, unique=True)
    descripcion = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        INACTIVO = "inactivo", "Inactivo"

    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ACTIVO, db_index=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="productos")
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name="productos")
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created", "-id"]

    def __str__(self):
        return self.nombre
