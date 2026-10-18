from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from gestion.models import Evento

from .factories import crear_evento, crear_instalacion, crear_usuario


class EventoApiTests(APITestCase):
    def setUp(self):
        self.usuario = crear_usuario()
        self.evento = crear_evento(self.usuario, titulo="Partido de pádel")
        crear_evento(self.usuario, titulo="Evento oculto", activo=False)
        self.url_lista = reverse("gestion:evento-api-list")

    def test_listado_publico_solo_con_eventos_activos(self):
        respuesta = self.client.get(self.url_lista)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        titulos = [e["titulo"] for e in respuesta.json()]
        self.assertEqual(titulos, ["Partido de pádel"])

    def test_campos_expuestos(self):
        respuesta = self.client.get(reverse("gestion:evento-api-detail", args=[self.evento.pk]))
        self.assertEqual(
            set(respuesta.json()),
            {"id", "titulo", "slug", "fecha_hora", "max_participantes", "activo"},
        )

    def test_anonimo_no_puede_borrar(self):
        respuesta = self.client.delete(reverse("gestion:evento-api-detail", args=[self.evento.pk]))
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Evento.objects.filter(pk=self.evento.pk).exists())

    def test_anonimo_no_puede_crear(self):
        crear_instalacion()
        respuesta = self.client.post(self.url_lista, {"titulo": "Nuevo"})
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)
