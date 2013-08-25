# -*- encoding: utf-8 -*-

from django import forms
from models import *
from django.contrib.admin.widgets import AdminDateWidget, AdminSplitDateTime
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.utils.safestring import mark_safe, SafeData

ATENCION = (
  (True,'Si'),
  (False,'No'),
)

class AgregarEmergenciaForm(forms.Form):
    ingreso          = forms.DateTimeField(label="Hora y Fecha de Ingreso",widget=forms.TextInput(attrs={'placeholder':'dd/MM/aaaa hh:mm:ss','data-format':'dd/MM/yyyy hh:mm:ss'}))
    cedula           = forms.CharField(label="Número de Cédula",max_length=9)
    nombres          = forms.CharField(label="Nombres", max_length=64)
    apellidos        = forms.CharField(label="Apellidos", max_length=64)
    sexo             = forms.ChoiceField(label="Sexo", choices=SEXO,required=False)
    fecha_nacimiento = forms.DateField(label="Fecha de Nacimiento",required=False)
    cel              = forms.CharField(label="Número de Teléfono Celular",max_length=11,required=False)
    email            = forms.EmailField(label="Correo Electrónico",max_length=64,required=False)
    direccion        = forms.CharField(label="Dirección",max_length=128,required=False)
    tlf_casa         = forms.CharField(label="Número de Teléfono de Habitación",max_length=11,required=False)    
    contacto_nombre  = forms.CharField(label="Nombre de la Persona de Contacto",max_length=64,required=False)
    contacto_rel     = forms.ChoiceField(label="Vínculo entre El Contacto y el Paciente",choices=RELACION,required=False)
    contacto_tlf     = forms.CharField(label="Número de Teléfono del Contacto",max_length=11,required=False)
    foto             = forms.ImageField(label="Foto",required=False)
    

class darAlta(forms.Form):
    destino  = forms.ModelChoiceField(label="Destino",queryset=Destino.objects.all())
    area     = forms.ModelChoiceField(label="Área de la Clínica a la que va",required=False,queryset=AreaAdmision.objects.all())
    darAlta  = forms.DateTimeField(label="Fecha y Hora en que se da De Alta")
    traslado = forms.DateTimeField(required=False)

class BuscarEmergenciaForm(forms.Form):
    cedula = forms.CharField(label="Número de Cédula",max_length=11,required=False)
    nombres = forms.CharField(label="Nombres",max_length=32,required=False)
    apellidos = forms.CharField(label="Apellidos",max_length=32,required=False)


class calcularTriageForm(forms.Form):
    fecha         = forms.DateTimeField(label="Fecha y hora a la que se realiza la Evaluación",widget=forms.TextInput(attrs={'placeholder':'dd/MM/aaaa hh:mm:ss','data-format':'dd/MM/yyyy hh:mm:ss'}))
    motivo        = forms.ModelChoiceField(label="Motivo de Ingreso",required=False,queryset=Motivo.objects.exclude(nombre__startswith=" "))
    ingreso       = forms.CharField(label="Tipo de Ingreso",required=False,max_length=1,widget=forms.Select(choices=ICAUSA))
    
    signos_tmp    = forms.FloatField(label="Temperatura",required=False)
    signos_fc     = forms.FloatField(label="Frecuencia Cardíaca",required=False)
    signos_fr     = forms.IntegerField(label="Frecuencia Respiratoria",required=False)
    signos_pa     = forms.IntegerField(label="Presión Sistólica / Alta",required=False)
    signos_pb     = forms.IntegerField(label="Presión Diastólica / Baja",required=False)
    signos_saod   = forms.FloatField(label="Saturación de Oxígeno",required=False)
    signos_avpu   = forms.CharField(label="Valor Obtenido en Escala AVPU",required=False,widget=forms.RadioSelect(choices=AVPU))
    signos_dolor  = forms.IntegerField(label="Intensidad del Dolor",required=False,widget=forms.Select(choices=EDOLOR))


##################################################### FORMS ATENCION

# Enfermedad Actual:
class AgregarEnfActual(forms.Form):
    narrativa = forms.CharField(widget=forms.widgets.Textarea)
    def __init__(self, *args, **kwargs):
      super(AgregarEnfActual, self).__init__(*args, **kwargs)
      self.fields['narrativa'].label = ""
      self.fields['narrativa'].widget.attrs['rows'] = 15
      # self.fields['narrativa'].widget.attrs['cols'] = 50


# Indicaciones - Dieta
class AgregarIndDietaForm(forms.Form):
  dieta     = forms.ModelChoiceField(queryset=Indicacion.objects.filter(tipo__iexact="dieta"),widget=forms.RadioSelect())
  observacion = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':5, 'cols':500}))
  # observacion = forms.CharField(widget=forms.widgets.Textarea())
  def __init__(self, *args, **kwargs):
    super(AgregarIndDietaForm, self).__init__(*args, **kwargs)
    self.fields['dieta'].empty_label = None
    self.fields['dieta'].label = "Tipo de Dieta:"


# Indicaciones - Hidratacion
class AgregarIndHidrataForm(forms.Form):
  hidrata     = forms.ModelChoiceField(label = "Tipo de Solución",required=True,queryset=Indicacion.objects.filter(tipo__iexact="hidrata"),widget=forms.RadioSelect())
  combina = forms.CharField(label = "¿Combinar con otro tipo de solución?:  ",widget=forms.RadioSelect(choices=ATENCION))
  combina_sol= forms.ModelChoiceField(label = "Tipo de Solución Adicional:  ",required=False,queryset=Indicacion.objects.filter(tipo__iexact="hidrata"),widget=forms.RadioSelect())
  volumen = forms.FloatField(label = "Volumen:  ",required=False)
  vel_inf = forms.CharField(label = "Velocidad de Infusión:  ",max_length=30)
  complementos = forms.CharField(label = "Complementos: ",max_length=40)
  def __init__(self, *args, **kwargs):
    super(AgregarIndHidrataForm, self).__init__(*args, **kwargs)
    self.fields['hidrata'].empty_label = None
    self.fields['combina_sol'].empty_label = None


# Indicaciones - Diagnosticas - Laboratorio
class AgregarIndLabForm(forms.Form):
  lab     = forms.ModelMultipleChoiceField(queryset=Indicacion.objects.filter(tipo__iexact="lab"),widget=CheckboxSelectMultiple)
  def __init__(self, *args, **kwargs):
    super(AgregarIndLabForm, self).__init__(*args, **kwargs)
    self.fields['lab'].empty_label = None
    self.fields['lab'].label = "Exámenes de Laboratorio:"


# Clase extra para agregar atributos a los elementos checkbox renderizados:
class MyCheckboxSelectMultiple(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        html = super(MyCheckboxSelectMultiple, self).render(name, value, attrs, choices)
        return mark_safe(html.replace('<ul>', '<ul class="imagen">'))


# Indicaciones - Diagnosticas - Imagenologia
class AgregarIndImgForm(forms.Form):
  imagen     = forms.ModelMultipleChoiceField(queryset=Indicacion.objects.filter(tipo__iexact="imagen"),widget=MyCheckboxSelectMultiple())
  def __init__(self, *args, **kwargs):
    super(AgregarIndImgForm, self).__init__(*args, **kwargs)
    self.fields['imagen'].empty_label = None
    self.fields['imagen'].label = "Tipos de exámenes:"


# Indicaciones - Diagnosticas - Est endoscopicos
class AgregarIndEndosForm(forms.Form):
  endoscopico     = forms.ModelMultipleChoiceField(queryset=Indicacion.objects.filter(tipo__iexact="endoscopico"),widget=CheckboxSelectMultiple)
  def __init__(self, *args, **kwargs):
    super(AgregarIndEndosForm, self).__init__(*args, **kwargs)
    # Para quitar la linea inicial (-----) del widget:
    self.fields['endoscopico'].empty_label = None
    self.fields['endoscopico'].label = "Exámenes Endoscópicos:"
