from rest_framework import serializers
from .models import Evento


class EventoSerializer(serializers.ModelSerializer):
    """Serializa los eventos para la API REST (EPD 07)."""
    class Meta:
        model = Evento
        fields = ['id', 'titulo', 'slug', 'fecha_hora', 'max_participantes', 'activo']
