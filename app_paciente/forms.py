import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django import forms
from models import *

from app_emergencia.forms import validate_nombre, validate_apellido,\
    validate_telefono

COD_TELEFONICOS = (
    ('0212', '0212'),
    ('0412', '0412'),
    ('0414', '0414'),
    ('0424', '0424'),
    ('0416', '0416'),
    ('0426', '0426'),
)


# def validate_nombre(value):
#     if re.match('^[a-zA-Z \']+$', value) is None:
#         raise ValidationError(
#             u'\"%s\" no es un nombre valido,\
#                 debe estar compuesto solo por letras.' % value)


# def validate_apellido(value):
#     if re.match('^[a-zA-Z \']+$', value) is None:
#         raise ValidationError(
#             u'\"%s\" no es un apellido valido,\
#                 debe estar compuesto solo por letras' % value)


# def validate_telefono(value):
#     if re.match('^[0-9]+[-]?[0-9]+$', value) is None:
#         raise ValidationError(u'\"%s\" no es un telefono valido' % value)


class AgregarPacienteForm(forms.Form):
    cedula = forms.CharField(max_length=9)
    nombres = forms.CharField(max_length=64, validators=[validate_nombre])
    apellidos = forms.CharField(max_length=64, validators=[validate_apellido])
    sexo = forms.ChoiceField(choices=SEXO)
    fecha_nacimiento = forms.DateField()
    cod_cel = forms.ChoiceField(choices=COD_TELEFONICOS)
    num_cel = forms.CharField(max_length=10, validators=[validate_telefono])
    email = forms.EmailField(max_length=50, error_messages={
        'invalid': ('La direccion de correo es invalida')
        }
    )
    direccion = forms.CharField(max_length=128)
    cod_tlf_casa = forms.ChoiceField(choices=COD_TELEFONICOS)
    num_tlf_casa = forms.CharField(
        max_length=10,
        validators=[validate_telefono])
    contacto_nombre = forms.CharField(
        max_length=80,
        validators=[validate_nombre])
    contacto_cod_tlf = forms.ChoiceField(choices=COD_TELEFONICOS)
    contacto_num_tlf = forms.CharField(
        max_length=10,
        validators=[validate_telefono])


class EditarPacienteForm(forms.Form):
    cedula = forms.CharField(
        required=True,
        label="Documento de Identidad")
    nombres = forms.CharField(
        max_length=64,
        validators=[validate_nombre])
    apellidos = forms.CharField(
        max_length=64,
        validators=[validate_apellido])
    email = forms.EmailField(
        required=False,
        max_length=50,
        error_messages={
            'invalid': ('La direccion de correo es invalida')
        }
    )
    fecha_nacimiento = forms.DateField(
        label="Fecha de Nacimiento",
        widget=forms.TextInput(
            attrs={
                'data-date-format': 'DD/MM/YYYY',
                }
            )
    )
