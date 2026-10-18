import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Evento, Perfil
from .forms import EventoForm, FormularioRegistro, PerfilForm
from .serializers import EventoSerializer


# ── API REST ─────────────────────────────────────────────────────────────────
class EventoViewSet(viewsets.ModelViewSet):
    """ViewSet que expone CRUD completo de Evento via API REST (EPD 07)."""
    queryset = Evento.objects.filter(activo=True).order_by('-fecha_hora')
    serializer_class = EventoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# ── REGISTRO ─────────────────────────────────────────────────────────────────
def registro(request):
    """Vista de registro de nuevas cuentas (EPD 06)."""
    if request.method == 'POST':
        form = FormularioRegistro(request.POST)
        if form.is_valid():
            nueva_cuenta = form.save(commit=False)
            nueva_cuenta.set_password(form.cleaned_data['password'])
            nueva_cuenta.save()
            # Creamos el perfil asociado automáticamente
            Perfil.objects.create(usuario=nueva_cuenta)
            login(request, nueva_cuenta)
            return redirect('gestion:lista_eventos')
    else:
        form = FormularioRegistro()
    return render(request, 'registration/registro.html', {'form': form})


# ── EVENTOS ───────────────────────────────────────────────────────────────────
def lista_eventos(request):
    """Lista todos los eventos activos con búsqueda por Q objects (EPD 05)."""
    query = request.GET.get('q')
    eventos = Evento.objects.filter(activo=True).order_by('-fecha_hora')
    if query:
        eventos = eventos.filter(
            Q(titulo__icontains=query) | Q(instalacion__sede__nombre__icontains=query)
        )
    return render(request, 'gestion/lista_eventos.html', {'eventos': eventos, 'query': query})


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
CLIMA_NO_DISPONIBLE = "No disponible"


def obtener_clima(latitud, longitud):
    """Devuelve la temperatura actual en la ubicación indicada usando Open-Meteo.

    Si la API falla, tarda más de 5 s o responde con un formato inesperado,
    devuelve "No disponible" para que la página de detalle nunca se rompa.
    """
    try:
        respuesta = requests.get(
            OPEN_METEO_URL,
            params={'latitude': latitud, 'longitude': longitud, 'current_weather': 'true'},
            timeout=5,
        )
        respuesta.raise_for_status()
        temperatura = respuesta.json()['current_weather']['temperature']
        return f"{temperatura} °C"
    except (requests.RequestException, KeyError, TypeError, ValueError):
        return CLIMA_NO_DISPONIBLE


def detalle_evento(request, evento_slug):
    """Detalle de evento con consumo de API Open-Meteo (EPD 08)."""
    evento = get_object_or_404(Evento, slug=evento_slug, activo=True)
    sede = evento.instalacion.sede
    clima = obtener_clima(sede.latitud, sede.longitud)
    return render(request, 'gestion/detalle_evento.html', {'evento': evento, 'clima': clima})


@login_required
def crear_evento(request):
    """Crear un nuevo evento (solo usuarios autenticados)."""
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            nuevo_evento = form.save(commit=False)
            nuevo_evento.organizador = request.user
            nuevo_evento.save()
            return redirect('gestion:detalle_evento', evento_slug=nuevo_evento.slug)
    else:
        form = EventoForm()
    return render(request, 'gestion/crear_evento.html', {'form': form})


@login_required
def editar_evento(request, evento_slug):
    """Editar evento — solo el organizador puede hacerlo."""
    evento = get_object_or_404(Evento, slug=evento_slug)
    if evento.organizador != request.user:
        return redirect('gestion:detalle_evento', evento_slug=evento_slug)
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            return redirect('gestion:detalle_evento', evento_slug=evento.slug)
    else:
        form = EventoForm(instance=evento)
    return render(request, 'gestion/editar_evento.html', {'form': form, 'evento': evento})


@login_required
def borrar_evento(request, evento_slug):
    """Borrar evento con confirmación — solo el organizador."""
    evento = get_object_or_404(Evento, slug=evento_slug)
    if evento.organizador != request.user:
        return redirect('gestion:detalle_evento', evento_slug=evento_slug)
    if request.method == 'POST':
        evento.delete()
        return redirect('gestion:lista_eventos')
    return render(request, 'gestion/confirmar_borrar_evento.html', {'evento': evento})


# ── PERFIL ────────────────────────────────────────────────────────────────────
@login_required
def ver_perfil(request):
    """Ver el perfil del usuario autenticado."""
    perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
    return render(request, 'gestion/perfil.html', {'perfil': perfil})


@login_required
def editar_perfil(request):
    """Editar bio y nivel del perfil — CRUD segunda entidad."""
    perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('gestion:ver_perfil')
    else:
        form = PerfilForm(instance=perfil)
    return render(request, 'gestion/editar_perfil.html', {'form': form})
