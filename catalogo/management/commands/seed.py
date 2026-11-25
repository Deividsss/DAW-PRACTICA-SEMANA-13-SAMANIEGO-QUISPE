from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from catalogo.models import Categoria, Producto

DATA = {
    "Cuadernos": ("Hojas gruesas que no sangran", [
        ("Cuaderno lavanda A5", "Tapa blanda, 120 hojas punteadas.", 24.90, 18),
        ("Libreta de bolsillo durazno", "Para listas rápidas y ideas sueltas.", 12.50, 30),
        ("Agenda 2027 menta", "Vista semanal, banda elástica.", 39.00, 9),
        ("Cuaderno de sueños", "Papel crema, sin líneas.", 27.00, 4),
    ]),
    "Washi y stickers": ("Para decorar cada página", [
        ("Washi tape nubes", "Rollo de 10 m, ancho 15 mm.", 8.90, 40),
        ("Pack stickers luna", "30 stickers resistentes al agua.", 11.00, 25),
        ("Washi tape flores secas", "Set de 3 rollos.", 15.50, 12),
        ("Stickers plantitas", "Hojas troqueladas.", 9.50, 0),
    ]),
    "Escritura": ("Tintas suaves, trazos firmes", [
        ("Gel pen pastel x6", "Punta 0.5 mm, colores suaves.", 18.00, 22),
        ("Resaltadores acuarela", "Set de 5 tonos translúcidos.", 21.50, 15),
        ("Lapicero fuente rosa", "Cartucho recargable.", 34.00, 3),
    ]),
    "Escritorio": ("Un rincón ordenado", [
        ("Organizador ondulado", "Cerámica esmaltada, 3 compartimentos.", 45.00, 7),
        ("Clips corazón x20", "Metal con baño pastel.", 6.50, 60),
        ("Bandeja de arcilla", "Hecha a mano, cada una es única.", 29.90, 5),
    ]),
}


class Command(BaseCommand):
    help = "Carga datos de ejemplo de DeiSam y un usuario demo."

    def handle(self, *args, **opts):
        User = get_user_model()
        user, created = User.objects.get_or_create(username="deisam")
        if created:
            user.set_password("deisam123")
            user.save()
        for nombre, (desc, productos) in DATA.items():
            cat, _ = Categoria.objects.get_or_create(nombre=nombre, defaults={"descripcion": desc})
            for n, d, p, s in productos:
                Producto.objects.get_or_create(
                    nombre=n, defaults=dict(descripcion=d, precio=p, stock=s, categoria=cat,
                                            estado="activo" if s else "inactivo", creado_por=user))
        self.stdout.write(self.style.SUCCESS("Datos cargados. Usuario demo: deisam / deisam123"))
