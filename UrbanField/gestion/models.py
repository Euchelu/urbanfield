from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Sede(models.Model):
    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=250)
    latitud = models.FloatField(help_text="Latitud para Open-Meteo")
    longitud = models.FloatField(help_text="Longitud para Open-Meteo")

    def __str__(self):
        return self.nombre

class Instalacion(models.Model):
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='instalaciones')
    nombre_pista = models.CharField(max_length=100)
    precio_hora = models.DecimalField(max_digits=6, decimal_places=2)
    es_cubierta = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre_pista} - {self.sede.nombre}"

class Evento(models.Model):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    instalacion = models.ForeignKey('Instalacion', on_delete=models.CASCADE)
    organizador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    max_participantes = models.PositiveIntegerField()
    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Si el slug está vacío, lo generamos a partir del título
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo

class Participacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    pagado = models.BooleanField(default=False)

    class Meta:
        unique_together = ('usuario', 'evento') # Un usuario no puede apuntarse dos veces

    def __str__(self):
        return f"{self.usuario.username} en {self.evento.titulo}"

class Perfil(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    nivel = models.CharField(max_length=50, default='Principiante')