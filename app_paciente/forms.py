from django import forms
from models import *

COD_TELEFONICOS = (
  ('0212','0212'),
  ('0412','0412'),
  ('0414','0414'),
  ('0424','0424'),
  ('0416','0416'),
  ('0426','0426'),
  )

class AgregarPacienteForm(forms.Form):
    cedula           = forms.CharField(max_length=9)
    nombres          = forms.CharField(max_length=64)
    apellidos        = forms.CharField(max_length=64)
    sexo             = forms.ChoiceField(choices=SEXO)
    fecha_nacimiento = forms.DateField()
    cod_cel          = forms.ChoiceField(choices=COD_TELEFONICOS)
    num_cel          = forms.CharField(max_length=7)
    email            = forms.EmailField(max_length=64)
    direccion        = forms.CharField(max_length=128)
    cod_tlf_casa     = forms.ChoiceField(choices=COD_TELEFONICOS)
    num_tlf_casa     = forms.CharField(max_length=7)    
    contacto_nombre  = forms.CharField(max_length=64)
    contacto_cod_tlf = forms.ChoiceField(choices=COD_TELEFONICOS)
    contacto_num_tlf = forms.CharField(max_length=11)


