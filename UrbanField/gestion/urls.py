from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para la API REST (EPD 07)
router = DefaultRouter()
router.register('eventos', views.EventoViewSet, basename='evento-api')

app_name = 'gestion'
urlpatterns = [
    # API REST
    path('api/', include(router.urls)),

    # Registro de usuario (EPD 06)
    path('registro/', views.registro, name='registro'),

    # Eventos — CRUD completo
    path('', views.lista_eventos, name='lista_eventos'),
    path('evento/nuevo/', views.crear_evento, name='crear_evento'),
    path('evento/<slug:evento_slug>/', views.detalle_evento, name='detalle_evento'),
    path('evento/<slug:evento_slug>/editar/', views.editar_evento, name='editar_evento'),
    path('evento/<slug:evento_slug>/borrar/', views.borrar_evento, name='borrar_evento'),

    # Perfil — segunda entidad con CRUD
    path('perfil/', views.ver_perfil, name='ver_perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
]
