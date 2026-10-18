"""Funciones auxiliares para crear datos de prueba de forma legible en los tests."""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone

from gestion.models import Evento, Instalacion, Sede

User = get_user_model()


def crear_usuario(username="ana", password="clave-segura-123"):
    return User.objects.create_user(username=username, password=password)


def crear_instalacion(nombre_pista="Pista 1"):
    sede = Sede.objects.create(
        nombre="Polideportivo San Pablo",
        direccion="C/ Ejemplo 1, Sevilla",
        latitud=37.39,
        longitud=-5.98,
    )
    return Instalacion.objects.create(
        sede=sede, nombre_pista=nombre_pista, precio_hora=Decimal("12.50")
    )


def crear_evento(organizador, titulo="Partido de pádel", instalacion=None, **extra):
    datos = {
        "titulo": titulo,
        "instalacion": instalacion or crear_instalacion(),
        "organizador": organizador,
        "fecha_hora": timezone.now() + timedelta(days=3),
        "max_participantes": 4,
    }
    datos.update(extra)
    return Evento.objects.create(**datos)
