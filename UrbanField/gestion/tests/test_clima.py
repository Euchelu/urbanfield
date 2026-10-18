from unittest.mock import Mock, patch

import requests
from django.test import SimpleTestCase

from gestion.views import CLIMA_NO_DISPONIBLE, obtener_clima


def respuesta_falsa(json_data=None, status_ok=True):
    respuesta = Mock()
    respuesta.json.return_value = json_data
    if not status_ok:
        respuesta.raise_for_status.side_effect = requests.HTTPError("500")
    return respuesta


@patch("gestion.views.requests.get")
class ObtenerClimaTests(SimpleTestCase):
    def test_devuelve_la_temperatura_formateada(self, mock_get):
        mock_get.return_value = respuesta_falsa({"current_weather": {"temperature": 24.5}})
        self.assertEqual(obtener_clima(37.39, -5.98), "24.5 °C")

    def test_envia_las_coordenadas_y_un_timeout(self, mock_get):
        mock_get.return_value = respuesta_falsa({"current_weather": {"temperature": 20}})
        obtener_clima(37.39, -5.98)
        _, kwargs = mock_get.call_args
        self.assertEqual(kwargs["params"]["latitude"], 37.39)
        self.assertEqual(kwargs["params"]["longitude"], -5.98)
        self.assertEqual(kwargs["timeout"], 5)

    def test_error_http_devuelve_no_disponible(self, mock_get):
        mock_get.return_value = respuesta_falsa(status_ok=False)
        self.assertEqual(obtener_clima(0, 0), CLIMA_NO_DISPONIBLE)

    def test_timeout_devuelve_no_disponible(self, mock_get):
        mock_get.side_effect = requests.Timeout()
        self.assertEqual(obtener_clima(0, 0), CLIMA_NO_DISPONIBLE)

    def test_respuesta_con_formato_inesperado_devuelve_no_disponible(self, mock_get):
        mock_get.return_value = respuesta_falsa({"otra_cosa": {}})
        self.assertEqual(obtener_clima(0, 0), CLIMA_NO_DISPONIBLE)
