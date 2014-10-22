from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django import forms
from models import *
from django.forms.widgets import CheckboxSelectMultiple
import re

COD_TELEFONICOS = (
    ('0212', '0212'),
    ('0412', '0412'),
    ('0414', '0414'),
    ('0424', '0424'),
    ('0416', '0416'),
    ('0426', '0426'),
)


def validate_nombre(value):
    if re.match('^[a-zA-Z \']+$', value) is None:
        raise ValidationError(
            u'\"%s\" no es un nombre valido,\
                debe estar compuesto solo por letras.' % value)


def validate_apellido(value):
    if re.match('^[a-zA-Z \']+$', value) is None:
        raise ValidationError(u'\"%s\" no es un apellido valido,\
            debe estar compuesto solo por letras' % value)


def validate_telefono(value):
    if re.match('^[0-9]+[-]?[0-9]+$', value) is None:
        raise ValidationError(u'\"%s\" no es un telefono valido' % value)


class IniciarSesionForm(forms.Form):
    unombre = forms.CharField(
        max_length=64,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Cedula de identidad:',
                'class': 'span2'}))
    uclave = forms.CharField(
        max_length=32,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Clave:',
                'class': 'span2'
            }
        )
    )


class SolicitarCuenta(forms.Form):
    cedula = forms.IntegerField(widget=forms.TextInput)
    nombres = forms.CharField(max_length=64, validators=[validate_nombre])
    apellidos = forms.CharField(max_length=64, validators=[validate_apellido])
    tipo = forms.ChoiceField(choices=USUARIO)
    sexo = forms.ChoiceField(choices=SEXO)
    cod_cel = forms.ChoiceField(
        choices=COD_TELEFONICOS,
        widget=forms.Select(
            attrs={'class': 'span1'}))
    num_cel = forms.CharField(
        max_length=7,
        widget=forms.TextInput(
            attrs={
                'class': 'span4'
            }
        ),
        validators=[validate_telefono])
    direccion = forms.CharField(max_length=128)
    cod_casa = forms.ChoiceField(
        choices=COD_TELEFONICOS,
        widget=forms.Select(
            attrs={'class': 'span1'}))
    num_casa = forms.CharField(
        max_length=7,
        widget=forms.TextInput(
            attrs={'class': 'span4'}),
        validators=[validate_telefono])
    email = forms.EmailField(
        max_length=50,
        error_messages={
            'invalid': ('La direccion de correo es invalida')})
    clave = forms.CharField(widget=forms.PasswordInput())
    clave0 = forms.CharField(widget=forms.PasswordInput())
    administrador = forms.BooleanField(required=False)


class cambioClave(forms.Form):
    claveV = forms.CharField(widget=forms.PasswordInput())
    clave = forms.CharField(widget=forms.PasswordInput())
    claveO = forms.CharField(widget=forms.PasswordInput())


class restablecerClave(forms.Form):
    correo = forms.EmailField(max_length=64)
