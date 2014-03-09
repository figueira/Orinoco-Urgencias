from django import forms
from models import *
from django.forms.widgets import CheckboxSelectMultiple

COD_TELEFONICOS = (
  ('0212','0212'),
  ('0412','0412'),
  ('0414','0414'),
  ('0424','0424'),
  ('0416','0416'),
  ('0426','0426'),
  )


class IniciarSesionForm(forms.Form):
    unombre = forms.CharField(
                      max_length = 64,
                      widget = forms.TextInput(
                                 attrs = {'placeholder': 'Cedula de identidad:',
                                          'class': 'span2'}))
    uclave = forms.CharField(max_length = 32,widget = forms.PasswordInput(attrs = {'placeholder':'Clave:','class':'span2'}))

class SolicitarCuenta(forms.Form):
    cedula = forms.IntegerField(widget=forms.TextInput)
    nombres = forms.CharField()
    apellidos = forms.CharField()
    tipo = forms.ChoiceField(choices = USUARIO)
    sexo = forms.ChoiceField(choices = SEXO)
    cod_cel = forms.ChoiceField(choices = COD_TELEFONICOS, widget=forms.Select(attrs={'class':'span1'}))
    num_cel = forms.CharField(max_length = 7, widget=forms.TextInput(attrs={'class':'span4'}))
    direccion = forms.CharField(max_length = 128)
    cod_casa = forms.ChoiceField(choices = COD_TELEFONICOS, widget=forms.Select(attrs={'class':'span1'}))
    num_casa = forms.CharField(max_length = 7, widget=forms.TextInput(attrs={'class':'span4'}))
    email = forms.EmailField(max_length = 64)
    clave = forms.CharField(widget = forms.PasswordInput())
    clave0 = forms.CharField(widget = forms.PasswordInput())
    administrador = forms.BooleanField(required = False)

class cambioClave(forms.Form):
    claveV = forms.CharField(widget = forms.PasswordInput())
    clave = forms.CharField(widget = forms.PasswordInput())
    claveO = forms.CharField(widget = forms.PasswordInput())

class restablecerClave(forms.Form):
    correo = forms.EmailField(max_length = 64)

