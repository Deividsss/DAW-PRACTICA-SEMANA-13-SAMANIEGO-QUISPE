from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, ProductoViewSet, api_root

router = DefaultRouter()
router.include_root_view = False
router.register("productos", ProductoViewSet, basename="producto")
router.register("categorias", CategoriaViewSet, basename="categoria")

urlpatterns = [
    path("", api_root, name="api-root"),
    path("", include(router.urls)),
]
