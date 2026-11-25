from django.contrib import admin
from .models import Categoria, Producto

admin.site.site_header = "DeiSam · Administración"

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "precio", "stock", "estado")
    list_filter = ("estado", "categoria")
    search_fields = ("nombre",)
