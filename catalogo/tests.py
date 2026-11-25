from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APIClient, APITestCase

from .models import Categoria, Producto


class DeiSamAPITests(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = get_user_model().objects.create_user("ana", password="x12345")
        self.cat = Categoria.objects.create(nombre="Cuadernos")
        for i in range(8):
            Producto.objects.create(nombre=f"Cuaderno {i}", precio=10 + i, stock=3, categoria=self.cat)

    def test_lista_paginada_y_filtrada(self):
        r = self.client.get("/api/productos/")
        self.assertEqual(r.data["count"], 8)
        self.assertEqual(len(r.data["results"]), 6)
        r = self.client.get("/api/productos/?precio_max=11&ordering=-precio")
        self.assertEqual(r.data["count"], 2)

    def test_hateoas(self):
        r = self.client.get("/api/productos/")
        self.assertIn("links", r.data["results"][0])
        self.assertIn("url", r.data["results"][0])

    def test_logout_en_home_autenticado(self):
        client = APIClient(enforce_csrf_checks=True)
        login_page = client.get("/api-auth/login/?next=/")
        self.assertEqual(login_page.status_code, 200)
        response = client.post(
            "/api-auth/login/?next=/",
            {
                "username": "ana",
                "password": "x12345",
                "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
            },
        )
        self.assertRedirects(response, "/")

        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'action="/api-auth/logout/"')

        response = client.post(
            "/api-auth/logout/",
            {"csrfmiddlewaretoken": client.cookies["csrftoken"].value},
        )
        self.assertRedirects(response, "/")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_validacion_stock_activo(self):
        self.client.force_authenticate(self.user)
        r = self.client.post("/api/productos/", {"nombre": "X", "precio": "5", "stock": 0,
                                                 "estado": "activo", "categoria": self.cat.pk})
        self.assertEqual(r.status_code, 400)
        self.assertIn("stock", r.data)

    def test_crear_requiere_login(self):
        r = self.client.post("/api/productos/", {})
        self.assertEqual(r.status_code, 403)

    def test_csrf_se_exige_con_sesion(self):
        c = APIClient(enforce_csrf_checks=True)
        c.login(username="ana", password="x12345")
        r = c.post("/api/productos/", {"nombre": "Y", "precio": "5", "stock": 2, "categoria": self.cat.pk})
        self.assertEqual(r.status_code, 403)

    def test_throttling_anonimo(self):
        from rest_framework.throttling import AnonRateThrottle
        with override_settings():
            AnonRateThrottle.THROTTLE_RATES = {"anon": "3/min"}
            AnonRateThrottle.rate = "3/min"
            codes = [self.client.get("/api/productos/").status_code for _ in range(5)]
        self.assertIn(429, codes)

    def test_docs_openapi(self):
        self.assertEqual(self.client.get("/api/schema/").status_code, 200)
        swagger = self.client.get("/api/docs/")
        self.assertEqual(swagger.status_code, 200)
        self.assertIn("swagger-ui-bundle.js", swagger.content.decode())

        redoc = self.client.get("/api/redoc/")
        self.assertEqual(redoc.status_code, 200)
        self.assertIn("redoc.standalone.js", redoc.content.decode())
        self.assertNotIn("cdn.jsdelivr.net", redoc.content.decode())
