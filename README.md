# DeiSam · API RESTful con Django REST Framework

Papelería suave para días largos. Proyecto de la Guía Práctica Semana 12 (IS093A).

## Instalación (Windows / VS Code)
```bash
python -m venv venv
venv\Scripts\activate          # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py seed          # datos de ejemplo + usuario deisam / deisam123
python manage.py runserver
```

## Rutas
| Ruta | Qué es |
|---|---|
| `/` | Tienda DeiSam (front que consume la API) |
| `/api/` | Raíz HATEOAS |
| `/api/productos/` · `/api/categorias/` | ViewSets (CRUD) |
| `/api/productos/destacados/` · `/api/productos/{id}/agotar/` | `@action` personalizadas |
| `/api/docs/` · `/api/redoc/` · `/api/schema/` | OpenAPI (drf-spectacular) |
| `/admin/` | Admin (`python manage.py createsuperuser`) |

## Pruebas rápidas
```bash
curl "http://127.0.0.1:8000/api/productos/?estado=activo&page=2&ordering=-created"
curl "http://127.0.0.1:8000/api/productos/?search=washi&precio_max=12"
curl "http://127.0.0.1:8000/api/categorias/?limit=2&offset=2"
curl -u deisam:deisam123 -X POST http://127.0.0.1:8000/api/productos/ \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Sello luna","precio":"14.50","stock":10,"estado":"activo","categoria":1}'
python manage.py test
```
