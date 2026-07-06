# UrbanField

Plataforma de gestión de eventos deportivos desarrollada con **Django 5.2**, orientada a la reserva de instalaciones urbanas (pistas de pádel, fútbol sala, etc.).

## Tecnologías

- Python 3.11 · Django 5.2
- Django REST Framework (API REST)
- PostgreSQL (producción) · SQLite (desarrollo local)
- Docker + Docker Compose + Nginx (despliegue)
- API Open-Meteo (clima en tiempo real)

## Funcionalidades

- Registro y autenticación de usuarios
- CRUD completo de eventos con slug único
- Búsqueda de eventos por título y sede (Q objects)
- Detalle de evento con temperatura en tiempo real (Open-Meteo)
- Perfil de usuario editable (bio, nivel)
- API REST con Django REST Framework (`/api/eventos/`)
- Despliegue con Docker Compose (Django + PostgreSQL + Nginx)

## Estructura

```
UrbanField/
├── gestion/               # App principal
│   ├── models.py          # Sede, Instalacion, Evento, Participacion, Perfil
│   ├── views.py           # Vistas y ViewSet API
│   ├── serializers.py
│   ├── forms.py
│   └── templates/
├── urbanfield_project/
│   └── settings/
│       ├── base.py        # Configuración común
│       ├── local.py       # Desarrollo (SQLite)
│       └── prod.py        # Producción (PostgreSQL)
├── templates/             # Base y registro
├── Dockerfile
├── docker-compose.yml
├── nginx/default.conf
└── requirements.txt
```

## Desarrollo local

```bash
cd UrbanField
cp .env.example .env        # Editar SECRET_KEY
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements
DJANGO_SETTINGS_MODULE=urbanfield_project.settings.local python manage.py migrate
DJANGO_SETTINGS_MODULE=urbanfield_project.settings.local python manage.py runserver
```

## Despliegue con Docker

```bash
cd UrbanField
cp .env.example .env        # Configurar credenciales reales
docker-compose up --build
```

La aplicación queda disponible en `http://localhost`.
