from django.contrib import admin
from .models import Sede, Instalacion, Evento, Participacion, Perfil


@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'latitud', 'longitud')
    search_fields = ('nombre', 'direccion')


@admin.register(Instalacion)
class InstalacionAdmin(admin.ModelAdmin):
    list_display = ('nombre_pista', 'sede', 'precio_hora', 'es_cubierta')
    list_filter = ('sede', 'es_cubierta')
    search_fields = ('nombre_pista',)


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_hora', 'instalacion', 'organizador', 'activo')
    list_filter = ('activo', 'fecha_hora', 'instalacion__sede')
    search_fields = ('titulo',)
    prepopulated_fields = {'slug': ('titulo',)}


@admin.register(Participacion)
class ParticipacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'evento', 'fecha_inscripcion', 'pagado')
    list_filter = ('pagado',)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'nivel')
    search_fields = ('usuario__username',)
