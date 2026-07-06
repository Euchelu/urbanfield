from django import forms
from django.contrib.auth import get_user_model
from .models import Evento, Perfil


# ── Formulario para crear y editar eventos ───────────────────────────────────
class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['titulo', 'instalacion', 'fecha_hora', 'max_participantes']
        widgets = {
            'fecha_hora': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


# ── Formulario de registro de nuevas cuentas (EPD 06) ────────────────────────
class FormularioRegistro(forms.ModelForm):
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repetir contraseña', widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name', 'email']
        help_texts = {'username': None}

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cd['password2']


# ── Formulario de edición de perfil ─────────────────────────────────────────
class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['bio', 'nivel']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
