"""Paso 2: serialización avanzada."""
from rest_framework import serializers
from rest_framework.reverse import reverse
from .models import Categoria, Producto


class CategoriaSerializer(serializers.HyperlinkedModelSerializer):
    """Representación hipervinculada (HATEOAS): enlaces en vez de ids sueltos."""
    url = serializers.HyperlinkedIdentityField(view_name="categoria-detail")
    productos_url = serializers.SerializerMethodField()
    total_productos = serializers.IntegerField(source="productos.count", read_only=True)

    class Meta:
        model = Categoria
        fields = ("id", "url", "nombre", "descripcion", "total_productos", "productos_url")

    def get_productos_url(self, obj) -> str:
        request = self.context["request"]
        return f"{reverse('producto-list', request=request)}?categoria={obj.pk}"


class ProductoSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="producto-detail")
    categoria_nombre = serializers.ReadOnlyField(source="categoria.nombre")      # campo read-only
    creado_por = serializers.ReadOnlyField(source="creado_por.username")          # sin exponer datos sensibles
    disponibilidad = serializers.SerializerMethodField()                          # campo calculado
    links = serializers.SerializerMethodField()                                   # HATEOAS básico

    class Meta:
        model = Producto
        fields = ("id", "url", "nombre", "descripcion", "precio", "stock", "estado",
                  "categoria", "categoria_nombre", "disponibilidad", "creado_por",
                  "created", "updated", "links")
        read_only_fields = ("created", "updated")

    def get_disponibilidad(self, obj) -> str:
        if obj.estado != Producto.Estado.ACTIVO:
            return "no disponible"
        if obj.stock == 0:
            return "agotado"
        return "pocas unidades" if obj.stock <= 5 else "disponible"

    def get_links(self, obj) -> dict:
        request = self.context["request"]
        return {
            "self": reverse("producto-detail", args=[obj.pk], request=request),
            "categoria": reverse("categoria-detail", args=[obj.categoria_id], request=request),
            "coleccion": reverse("producto-list", request=request),
        }

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0.")
        return value

    def validate(self, attrs):
        """Validación anidada entre campos (funciona también con PATCH)."""
        estado = attrs.get("estado", getattr(self.instance, "estado", Producto.Estado.ACTIVO))
        stock = attrs.get("stock", getattr(self.instance, "stock", 0))
        if estado == Producto.Estado.ACTIVO and stock == 0:
            raise serializers.ValidationError(
                {"stock": "Un producto activo necesita al menos 1 unidad. Márcalo como inactivo o sube el stock."})
        return attrs
