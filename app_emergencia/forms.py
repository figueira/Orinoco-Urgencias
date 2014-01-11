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
    ingreso = forms.DateTimeField(
                label = "FECHA Y HORA DE INGRESO",
                widget = forms.TextInput(attrs = {'placeholder':'dd/MM/aaaa hh:mm:ss','data-format':'dd/MM/yyyy hh:mm:ss'}))
    cedula = forms.CharField(label = "DOCUMENTO DE IDENTIDAD")
    nombres = forms.CharField(label = "NOMBRE", max_length = 64)
    apellidos = forms.CharField(label = "APELLIDO", max_length = 64)
    sexo = forms.ChoiceField(label = "SEXO", choices = SEXO,required = False)
    fecha_nacimiento = forms.DateField(label = "FECHA DE NACIMIENTO")

class darAlta(forms.Form):
    destino  = forms.ModelChoiceField(label="Destino",queryset=Destino.objects.all())
    area     = forms.ModelChoiceField(label="Área de la Clínica a la que va",required=False,queryset=AreaAdmision.objects.all())
    darAlta  = forms.DateTimeField(label="Fecha y Hora en que se da De Alta")
    traslado = forms.DateTimeField(required=False)

class BuscarEmergenciaForm(forms.Form):
    cedula = forms.CharField(label="Número de Cédula",max_length=11,required=False)
    nombres = forms.CharField(label="Nombres",max_length=32,required=False)
    apellidos = forms.CharField(label="Apellidos",max_length=32,required=False)


class FormularioEvaluacionPaciente(forms.Form):
    avpu = forms.CharField(label = "Escala AVPU",
                           widget = forms.RadioSelect(choices = AVPU))
    fecha = forms.DateTimeField(
                    label = "Fecha y hora a la que se realiza la Evaluación",
                    widget = forms.TextInput(
                                     attrs = 
                                       {'placeholder':'dd/MM/aaaa hh:mm:ss',
                                        'data-format':'dd/MM/yyyy hh:mm:ss'}))
    frecuencia_cardiaca = forms.FloatField(label = "Frecuencia cardíaca")
    frecuencia_respiratoria = forms.IntegerField(label = "Frecuencia respiratoria")

    ingreso = forms.CharField(label = "Tipo de ingreso",
                              max_length = 1,
                              widget = forms.Select(choices = ICAUSA))
    
    intensidad_dolor = forms.IntegerField(
                               label = "Intensidad del dolor",
                               widget = forms.Select(choices = EDOLOR))
    motivo = forms.ModelChoiceField(
                     label = "Motivo de ingreso",
                     queryset = Motivo.objects.exclude(
                                                 nombre__startswith = " "))
    presion_sistolica = forms.IntegerField(label = "Presión sistólica")
    presion_diastolica = forms.IntegerField(label = "Presión diastólica")
    saturacion_oxigeno = forms.FloatField(label = "Saturación de oxígeno")
    temperatura = forms.FloatField()

    # Validaciones perzonalizadas sobre los campos del formulario
    def clean_frecuencia_cardiaca(self):
      self.__validar_intervalo(self.cleaned_data['frecuencia_cardiaca'], 0, 200)
      return self.cleaned_data['frecuencia_cardiaca']

    def clean_frecuencia_respiratoria(self):
      self.__validar_intervalo(self.cleaned_data['frecuencia_respiratoria'],
                               0,
                               30)
      return self.cleaned_data['frecuencia_respiratoria']

    def clean_presion_diastolica(self):
      self.__validar_intervalo(self.cleaned_data['presion_diastolica'], 0, 200)
      return self.cleaned_data['presion_diastolica']

    def clean_presion_sistolica(self):
      self.__validar_intervalo(self.cleaned_data['presion_sistolica'], 0, 300)
      return self.cleaned_data['presion_sistolica']

    def clean_saturacion_oxigeno(self):
      self.__validar_intervalo(self.cleaned_data['saturacion_oxigeno'], 0, 100)
      return self.cleaned_data['saturacion_oxigeno']

    def clean_temperatura(self):
      self.__validar_intervalo(self.cleaned_data['temperatura'], 36, 42)
      return self.cleaned_data['temperatura']

    # Metodos privados

    def __validar_intervalo(self, valor, limite_inferior, limite_superior):
      if valor < limite_inferior or limite_superior < valor:
        raise forms.ValidationError('Debe estar entre ' + str(limite_inferior) +
                                    ' y ' + str(limite_superior))

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
