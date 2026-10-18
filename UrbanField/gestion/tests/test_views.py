from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from gestion.models import Evento, Perfil

from .factories import crear_evento, crear_instalacion, crear_usuario

User = get_user_model()


class ListaEventosTests(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()
        self.padel = crear_evento(self.usuario, titulo="Partido de pádel")
        self.futbol = crear_evento(self.usuario, titulo="Fútbol sala")
        self.inactivo = crear_evento(self.usuario, titulo="Evento cancelado", activo=False)

    def test_muestra_solo_eventos_activos(self):
        respuesta = self.client.get(reverse("gestion:lista_eventos"))
        self.assertEqual(respuesta.status_code, 200)
        eventos = list(respuesta.context["eventos"])
        self.assertIn(self.padel, eventos)
        self.assertIn(self.futbol, eventos)
        self.assertNotIn(self.inactivo, eventos)

    def test_busqueda_por_titulo(self):
        respuesta = self.client.get(reverse("gestion:lista_eventos"), {"q": "pádel"})
        self.assertEqual(list(respuesta.context["eventos"]), [self.padel])

    def test_busqueda_por_sede(self):
        respuesta = self.client.get(reverse("gestion:lista_eventos"), {"q": "San Pablo"})
        self.assertEqual(len(respuesta.context["eventos"]), 2)


@patch("gestion.views.obtener_clima", return_value="21 °C")
class DetalleEventoTests(TestCase):
    def setUp(self):
        self.organizador = crear_usuario("organizador")
        self.evento = crear_evento(self.organizador)

    def test_muestra_el_evento_y_el_clima(self, _mock_clima):
        respuesta = self.client.get(reverse("gestion:detalle_evento", args=[self.evento.slug]))
        self.assertContains(respuesta, "Partido de pádel")
        self.assertContains(respuesta, "21 °C")

    def test_evento_inactivo_devuelve_404(self, _mock_clima):
        self.evento.activo = False
        self.evento.save()
        respuesta = self.client.get(reverse("gestion:detalle_evento", args=[self.evento.slug]))
        self.assertEqual(respuesta.status_code, 404)

    def test_solo_el_organizador_ve_los_botones_de_edicion(self, _mock_clima):
        url = reverse("gestion:detalle_evento", args=[self.evento.slug])
        enlace_editar = reverse("gestion:editar_evento", args=[self.evento.slug])

        self.assertNotContains(self.client.get(url), enlace_editar)

        self.client.force_login(self.organizador)
        self.assertContains(self.client.get(url), enlace_editar)


class CrearEventoTests(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()
        self.instalacion = crear_instalacion()
        self.url = reverse("gestion:crear_evento")

    def test_requiere_iniciar_sesion(self):
        respuesta = self.client.get(self.url)
        self.assertRedirects(respuesta, f"{reverse('login')}?next={self.url}")

    def test_crea_el_evento_con_el_usuario_como_organizador(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.post(self.url, {
            "titulo": "Quedada de baloncesto",
            "instalacion": self.instalacion.pk,
            "fecha_hora": "2030-05-10T18:00",
            "max_participantes": 10,
        })
        evento = Evento.objects.get(titulo="Quedada de baloncesto")
        self.assertEqual(evento.organizador, self.usuario)
        self.assertRedirects(respuesta, reverse("gestion:detalle_evento", args=[evento.slug]),
                             fetch_redirect_response=False)


class EditarYBorrarEventoTests(TestCase):
    def setUp(self):
        self.organizador = crear_usuario("organizador")
        self.otro = crear_usuario("intruso")
        self.evento = crear_evento(self.organizador)
        self.url_editar = reverse("gestion:editar_evento", args=[self.evento.slug])
        self.url_borrar = reverse("gestion:borrar_evento", args=[self.evento.slug])
        self.datos = {
            "titulo": "Título cambiado",
            "instalacion": self.evento.instalacion.pk,
            "fecha_hora": "2030-05-10T18:00",
            "max_participantes": 8,
        }

    def test_el_organizador_puede_editar(self):
        self.client.force_login(self.organizador)
        self.client.post(self.url_editar, self.datos)
        self.evento.refresh_from_db()
        self.assertEqual(self.evento.titulo, "Título cambiado")

    def test_otro_usuario_no_puede_editar(self):
        self.client.force_login(self.otro)
        self.client.post(self.url_editar, self.datos)
        self.evento.refresh_from_db()
        self.assertEqual(self.evento.titulo, "Partido de pádel")

    def test_el_organizador_puede_borrar(self):
        self.client.force_login(self.organizador)
        self.client.post(self.url_borrar)
        self.assertFalse(Evento.objects.filter(pk=self.evento.pk).exists())

    def test_otro_usuario_no_puede_borrar(self):
        self.client.force_login(self.otro)
        self.client.post(self.url_borrar)
        self.assertTrue(Evento.objects.filter(pk=self.evento.pk).exists())

    def test_get_en_borrar_pide_confirmacion_sin_borrar(self):
        self.client.force_login(self.organizador)
        respuesta = self.client.get(self.url_borrar)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(Evento.objects.filter(pk=self.evento.pk).exists())


class RegistroTests(TestCase):
    url = reverse("gestion:registro")

    def datos(self, **extra):
        datos = {
            "username": "nuevo",
            "first_name": "Nuevo",
            "last_name": "Usuario",
            "email": "nuevo@example.com",
            "password": "clave-segura-123",
            "password2": "clave-segura-123",
        }
        datos.update(extra)
        return datos

    def test_registro_crea_usuario_perfil_e_inicia_sesion(self):
        respuesta = self.client.post(self.url, self.datos())
        usuario = User.objects.get(username="nuevo")
        self.assertTrue(usuario.check_password("clave-segura-123"))
        self.assertTrue(Perfil.objects.filter(usuario=usuario).exists())
        self.assertEqual(int(self.client.session["_auth_user_id"]), usuario.pk)
        self.assertRedirects(respuesta, reverse("gestion:lista_eventos"))

    def test_contrasenas_distintas_no_crean_usuario(self):
        respuesta = self.client.post(self.url, self.datos(password2="otra-clave-456"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(User.objects.filter(username="nuevo").exists())
        self.assertContains(respuesta, "Las contraseñas no coinciden.")


class PerfilTests(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()
        self.client.force_login(self.usuario)

    def test_ver_perfil_lo_crea_si_no_existe(self):
        respuesta = self.client.get(reverse("gestion:ver_perfil"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(Perfil.objects.filter(usuario=self.usuario).exists())

    def test_editar_perfil(self):
        self.client.post(reverse("gestion:editar_perfil"), {"bio": "Me gusta el pádel", "nivel": "Avanzado"})
        perfil = Perfil.objects.get(usuario=self.usuario)
        self.assertEqual(perfil.bio, "Me gusta el pádel")
        self.assertEqual(perfil.nivel, "Avanzado")
