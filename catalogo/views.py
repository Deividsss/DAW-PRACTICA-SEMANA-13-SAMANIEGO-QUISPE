"""Pasos 3 y 4: ViewSets, filtrado, paginación y throttling."""
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .filters import ProductoFilter
from .models import Categoria, Producto
from .serializers import CategoriaSerializer, ProductoSerializer


@ensure_csrf_cookie  # entrega la cookie csrftoken que usa el fetch() del front
def home(request):
    return render(request, "index.html")


@api_view(["GET"])
def api_root(request, format=None):
    """Punto de entrada HATEOAS: la API se navega sola."""
    return Response({
        "productos": reverse("producto-list", request=request),
        "categorias": reverse("categoria-list", request=request),
        "documentacion": reverse("swagger-ui", request=request),
        "esquema_openapi": reverse("schema", request=request),
    })


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    pagination_class = LimitOffsetPagination      # ?limit=2&offset=2
    search_fields = ["nombre"]
    ordering_fields = ["nombre"]


class ProductoViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoSerializer
    filterset_class = ProductoFilter              # ?estado=activo&categoria=1&precio_max=20
    search_fields = ["nombre", "descripcion"]     # ?search=washi
    ordering_fields = ["precio", "created", "nombre", "stock"]  # ?ordering=-created
    # PageNumberPagination global: ?page=2

    def get_queryset(self):
        # select_related evita consultas N+1; los filtros se aplican en la BD (lazy)
        return Producto.objects.select_related("categoria", "creado_por")

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)

    @action(detail=False, methods=["get"])
    def destacados(self, request):
        """Los 3 productos activos más recientes con stock."""
        qs = self.get_queryset().filter(estado="activo", stock__gt=0)[:3]
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=True, methods=["post"])
    def agotar(self, request, pk=None):
        """Deja el stock en 0 y desactiva el producto."""
        producto = self.get_object()
        producto.stock, producto.estado = 0, Producto.Estado.INACTIVO
        producto.save(update_fields=["stock", "estado", "updated"])
        return Response(self.get_serializer(producto).data, status=status.HTTP_200_OK)
