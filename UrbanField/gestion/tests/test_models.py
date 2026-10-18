from django.db import IntegrityError
from django.test import TestCase

from gestion.models import Participacion

from .factories import crear_evento, crear_instalacion, crear_usuario


class EventoModelTests(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()

    def test_genera_slug_a_partir_del_titulo(self):
        evento = crear_evento(self.usuario, titulo="Torneo Fútbol Sala")
        self.assertEqual(evento.slug, "torneo-futbol-sala")

    def test_slug_unico_con_titulos_repetidos(self):
        instalacion = crear_instalacion()
        primero = crear_evento(self.usuario, titulo="Partido", instalacion=instalacion)
        segundo = crear_evento(self.usuario, titulo="Partido", instalacion=instalacion)
        tercero = crear_evento(self.usuario, titulo="Partido", instalacion=instalacion)
        self.assertEqual(
            [primero.slug, segundo.slug, tercero.slug],
            ["partido", "partido-2", "partido-3"],
        )

    def test_conserva_el_slug_al_editar(self):
        evento = crear_evento(self.usuario, titulo="Partido")
        evento.titulo = "Partido modificado"
        evento.save()
        evento.refresh_from_db()
        self.assertEqual(evento.slug, "partido")

    def test_titulo_sin_caracteres_validos_genera_slug_por_defecto(self):
        evento = crear_evento(self.usuario, titulo="!!!")
        self.assertEqual(evento.slug, "evento")

    def test_representacion_en_texto(self):
        evento = crear_evento(self.usuario, titulo="Partido de pádel")
        self.assertEqual(str(evento), "Partido de pádel")
        self.assertEqual(str(evento.instalacion), "Pista 1 - Polideportivo San Pablo")


class ParticipacionModelTests(TestCase):
    def test_un_usuario_no_puede_apuntarse_dos_veces(self):
        usuario = crear_usuario()
        evento = crear_evento(usuario)
        Participacion.objects.create(usuario=usuario, evento=evento)
        with self.assertRaises(IntegrityError):
            Participacion.objects.create(usuario=usuario, evento=evento)
