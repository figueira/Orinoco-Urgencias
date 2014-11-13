# -*- encoding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.admin.widgets import AdminDateWidget, AdminSplitDateTime
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.utils.safestring import mark_safe, SafeData
from django.db.models import Q
from django import forms

from models import *

import re

DocumentoIdentidad = (
    ('V-', 'Cedula'),
    ('E-', 'Extranjero'),
    ('P-', 'Pasaporte'),
)

ATENCION = (
    (True, 'Si'),
    (False, 'No'),
)

UNDIDAD = (
    ('gotas/min', 'gotas/min'),
    ('cc/hora', 'cc/hora'),
)


def validate_nombre(value):
    if re.match('^[a-zA-Z \']+$', value) is None:
        raise ValidationError(
            u'\"%s\" no es un nombre valido, debe estar\
            compuesto solo por letras.' % value)


def validate_apellido(value):
    if re.match('^[a-zA-Z \']+$', value) is None:
        raise ValidationError(u'\"%s\" no es un apellido valido,\
        debe estar compuesto solo por letras' % value)


def validate_telefono(value):
    if re.match('^[0-9]+[-]?[0-9]+$', value) is None:
        raise ValidationError(u'\"%s\" no es un telefono valido' % value)


def validate_dolor(value):
    if value > 10:
        raise ValidationError(u'\"%s\" intensidad maxima es de 10' % value)


class AgregarEmergenciaForm(forms.Form):
    ingreso = forms.DateTimeField(
        required=True,
        label="FECHA Y HORA DE INGRESO",
        widget=forms.TextInput(
            attrs={
                'placeholder': 'DD/MM/YYYY hh:mm:ss',
                'data-date-format': 'DD/MM/YYYY HH:mm:ss',
                }
            )
    )
    documento = forms.ChoiceField(choices=DocumentoIdentidad)
    cedula = forms.CharField(
        required=True,
        label="DOCUMENTO DE IDENTIDAD")
    nombres = forms.CharField(
        label="NOMBRE",
        required=True,
        max_length=64,
        validators=[validate_nombre]
    )
    apellidos = forms.CharField(
        label="APELLIDO",
        required=True,
        max_length=64,
        validators=[validate_apellido]
    )
    sexo = forms.ChoiceField(
        label="SEXO",
        choices=SEXO,
        required=False
    )
    fecha_nacimiento = forms.DateField(
        label="FECHA DE NACIMIENTO",
        widget=forms.TextInput(
            attrs={
                'data-date-format': 'DD/MM/YYYY',
                }
            )
    )


class darAlta(forms.Form):
    destino = forms.ModelChoiceField(
        label="Destino",
        queryset=Destino.objects.all()
    )
    area = forms.ModelChoiceField(
        label="Area",
        required=False,
        queryset=AreaAdmision.objects.all()
    )
    darAlta = forms.DateTimeField(
        label="Fecha y Hora",
        widget=forms.TextInput(
            attrs={
                'placeholder': 'DD/MM/YYYY hh:mm:ss',
                'data-date-format': 'DD/MM/YYYY HH:mm:ss',
                }
        )
    )
    traslado = forms.DateTimeField(required=False)


class BuscarEmergenciaForm(forms.Form):
    cedula = forms.CharField(
        label="Número de Cédula",
        max_length=11,
        required=False
    )
    nombres = forms.CharField(
        label="Nombres",
        min_length=3,
        max_length=32,
        required=False,
        validators=[validate_nombre]
    )
    apellidos = forms.CharField(
        label="Apellidos",
        min_length=3,
        max_length=32,
        required=False,
        validators=[validate_apellido]
    )


class FormularioEvaluacionPaciente(forms.Form):
    avpu = forms.CharField(
        label="Escala AVPU",
        widget=forms.RadioSelect(
            choices=AVPU)
    )
    fecha = forms.DateTimeField(
        label="Fecha y Hora",
        widget=forms.TextInput(
            attrs={
                'placeholder': 'DD/MM/YYYY hh:mm:ss',
                'data-date-format': 'DD/MM/YYYY HH:mm:ss',
                }
        )
    )
    frecuencia_cardiaca = forms.IntegerField(
        label="Frecuencia cardíaca",
        min_value=0,
        max_value=200,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    frecuencia_respiratoria = forms.IntegerField(
        label="Frecuencia respiratoria",
        min_value=0,
        max_value=30,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    ingreso = forms.CharField(
        label="Tipo de ingreso",
        max_length=1,
        widget=forms.Select(
            choices=ICAUSA)
        )
    intensidad_dolor = forms.IntegerField(
        label="Intensidad del dolor",
        widget=forms.Select(
            choices=EDOLOR)
        )
    motivo = forms.ModelChoiceField(
        label="Motivo de ingreso",
        queryset=Motivo.objects.exclude(
            nombre__startswith=" ").order_by('pk')
        )
    presion_sistolica = forms.IntegerField(
        label="Presión sistólica",
        min_value=0,
        max_value=300,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    presion_diastolica = forms.IntegerField(
        label="Presión diastólica",
        min_value=0,
        max_value=200,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    saturacion_oxigeno = forms.IntegerField(
        label="Saturación de oxígeno",
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    temperatura = forms.FloatField(
        min_value=36,
        max_value=42,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    # Validaciones perzonalizadas sobre los campos del formulario
    def clean_frecuencia_cardiaca(self):
        self.__validar_intervalo(
            self.cleaned_data['frecuencia_cardiaca'], 0, 200)
        return self.cleaned_data['frecuencia_cardiaca']

    def clean_frecuencia_respiratoria(self):
        self.__validar_intervalo(
            self.cleaned_data['frecuencia_respiratoria'], 0, 30)
        return self.cleaned_data['frecuencia_respiratoria']

    def clean_presion_diastolica(self):
        self.__validar_intervalo(self.cleaned_data[
            'presion_diastolica'], 0, 200)
        return self.cleaned_data['presion_diastolica']

    def clean_presion_sistolica(self):
        self.__validar_intervalo(self.cleaned_data[
            'presion_sistolica'], 0, 300)
        return self.cleaned_data['presion_sistolica']

    def clean_saturacion_oxigeno(self):
        self.__validar_intervalo(self.cleaned_data[
            'saturacion_oxigeno'], 0, 100)
        return self.cleaned_data['saturacion_oxigeno']

    def clean_temperatura(self):
        self.__validar_intervalo(self.cleaned_data[
            'temperatura'], 36, 42)
        return self.cleaned_data['temperatura']

    # Metodos privados

    def __validar_intervalo(self, valor, limite_inferior, limite_superior):
        if valor < limite_inferior or limite_superior < valor:
            raise forms.ValidationError(
                'Debe estar entre ' + str(limite_inferior) +
                ' y ' + str(limite_superior)
            )


class ActualizarSignosForm(forms.Form):
    avpu = forms.CharField(
        label="Escala AVPU",
        widget=forms.RadioSelect(
            choices=AVPU)
        )
    frecuencia_cardiaca = forms.IntegerField(
        label="Frecuencia cardíaca",
        min_value=0,
        max_value=200
    )
    frecuencia_respiratoria = forms.IntegerField(
        label="Frecuencia respiratoria",
        min_value=0,
        max_value=30
    )
    intensidad_dolor = forms.IntegerField(
        label="Intensidad del dolor",
        widget=forms.Select(
            choices=EDOLOR
        )
    )
    presion_sistolica = forms.IntegerField(
        label="Presión sistólica",
        min_value=0,
        max_value=300
    )
    presion_diastolica = forms.IntegerField(
        label="Presión diastólica",
        min_value=0,
        max_value=200
    )
    saturacion_oxigeno = forms.IntegerField(
        label="Saturación de oxígeno",
        min_value=0,
        max_value=100
    )
    temperatura = forms.FloatField(
        min_value=0, max_value=45
    )

    # Validaciones perzonalizadas sobre los campos del formulario
    def clean_frecuencia_cardiaca(self):
        self.__validar_intervalo(
            self.cleaned_data['frecuencia_cardiaca'], 0, 200)
        return self.cleaned_data['frecuencia_cardiaca']

    def clean_frecuencia_respiratoria(self):
        self.__validar_intervalo(self.cleaned_data[
            'frecuencia_respiratoria'], 0, 30)
        return self.cleaned_data['frecuencia_respiratoria']

    def clean_presion_diastolica(self):
        self.__validar_intervalo(self.cleaned_data[
            'presion_diastolica'], 0, 200)
        return self.cleaned_data['presion_diastolica']

    def clean_presion_sistolica(self):
        self.__validar_intervalo(self.cleaned_data[
            'presion_sistolica'], 0, 300)
        return self.cleaned_data['presion_sistolica']

    def clean_saturacion_oxigeno(self):
        self.__validar_intervalo(self.cleaned_data[
            'saturacion_oxigeno'], 0, 100)
        return self.cleaned_data['saturacion_oxigeno']

    def clean_temperatura(self):
        self.__validar_intervalo(self.cleaned_data[
            'temperatura'], 36, 42)
        return self.cleaned_data['temperatura']

    # Metodos privados

    def __validar_intervalo(self, valor, limite_inferior, limite_superior):
        if valor < limite_inferior or limite_superior < valor:
            raise forms.ValidationError(
                'Debe estar entre ' + str(limite_inferior) +
                ' y ' + str(limite_superior))


#  FORMS ATENCION

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
    dieta = forms.ModelChoiceField(
        queryset=Indicacion.objects.filter(
            tipo__iexact="dieta"), widget=forms.RadioSelect()
    )
    observacion = forms.CharField(
        required=False,
        widget=forms.widgets.Textarea(
            attrs={
                'rows': 5,
                'cols': 500
            }
        )
    )

    # observacion = forms.CharField(widget=forms.widgets.Textarea())
    def __init__(self, *args, **kwargs):
        super(AgregarIndDietaForm, self).__init__(*args, **kwargs)
        self.fields['dieta'].empty_label = None
        self.fields['dieta'].label = "Tipo de Dieta:"


# Indicaciones - Hidratacion
class AgregarIndHidrataForm(forms.Form):
    hidrata = forms.ModelChoiceField(
        label="Tipo de Solución",
        required=True,
        queryset=Indicacion.objects.filter(
            tipo__iexact="hidrata"), widget=forms.RadioSelect())
    combina = forms.CharField(
        label="¿Combinar con otro tipo de solución?:  ",
        widget=forms.RadioSelect(choices=ATENCION))
    combina_sol = forms.ModelChoiceField(
        label="Tipo de Solución Adicional:  ",
        required=False,
        queryset=Indicacion.objects.filter(
            tipo__iexact="hidrata"), widget=forms.RadioSelect())
    volumen = forms.FloatField(
        label="Volumen:  ",
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'span1'
            }
        )
    )
    vel_inf = forms.CharField(
        label="Velocidad de Infusión:  ",
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'class': 'width40'
            }
        )
    )
    vel_inf_unidad = forms.ChoiceField(
        choices=UNDIDAD,
        widget=forms.Select(
            attrs={
                'class': 'width100'
            }
        )
    )
    complementos = forms.CharField(
        label="Complementos: ",
        required=False,
        max_length=40,
        widget=forms.widgets.Textarea(
            attrs={
                'rows': 2,
                'cols': 20
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super(AgregarIndHidrataForm, self).__init__(*args, **kwargs)
        self.fields['hidrata'].empty_label = None
        self.fields['combina_sol'].empty_label = None


# Indicaciones - Diagnosticas - Laboratorio
class AgregarIndLabForm(forms.Form):
    lab = forms.ModelMultipleChoiceField(
        queryset=Indicacion.objects.filter(tipo__iexact="lab"),
        widget=CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        super(AgregarIndLabForm, self).__init__(*args, **kwargs)
        self.fields['lab'].empty_label = None
        self.fields['lab'].label = "Exámenes de Laboratorio:"


# Clase extra para agregar atributos a los elementos checkbox renderizados:
class MyCheckboxSelectMultiple(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        html = super(
            MyCheckboxSelectMultiple, self).render(name, value, attrs, choices)
        return mark_safe(html.replace('<ul', '<ul class="imagen"'))


# Clase extra para agregar atributos a los elementos checkbox renderizados:
class MyCheckboxSelectMultipleEndos(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        html = super(
            MyCheckboxSelectMultipleEndos, self).render(
            name, value, attrs, choices)
        return mark_safe(html.replace('<ul', '<ul class="endoscopico"'))


# Indicaciones - Diagnosticas - Imagenologia
class AgregarIndImgForm(forms.Form):
    imagen = forms.ModelMultipleChoiceField(
        queryset=Indicacion.objects.filter(
            tipo__iexact="imagen"), widget=MyCheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        super(AgregarIndImgForm, self).__init__(*args, **kwargs)
        self.fields['imagen'].empty_label = None
        self.fields['imagen'].label = "Tipos de exámenes:"


# Indicaciones - Diagnosticas - Est endoscopicos
class AgregarIndEndosForm(forms.Form):
    endoscopico = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Indicacion.objects.filter(
            Q(tipo="endoscopico"),
            ~Q(nombre="Arterografia"),
            ~Q(nombre="Otros")),
        widget=CheckboxSelectMultiple)
    otros = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Indicacion.objects.filter(
            Q(tipo="endoscopico"),
            Q(nombre="Arterografia") | Q(nombre="Otros")),
        widget=MyCheckboxSelectMultipleEndos())

    def __init__(self, *args, **kwargs):
        super(AgregarIndEndosForm, self).__init__(*args, **kwargs)
        # Para quitar la linea inicial (-----) del widget:
        self.fields['endoscopico'].empty_label = None
        self.fields['endoscopico'].label = "Exámenes Especiales:"


class buscar_por_cedulaForm(forms.Form):
    documento = forms.ChoiceField(choices=DocumentoIdentidad)
    cedula = forms.IntegerField(required=True, min_value=999)


class buscar_por_nombreForm(forms.Form):
    nombre = forms.CharField(
        min_length=4,
        max_length=20,
        required=False
    )
    apellido = forms.CharField(
        min_length=4,
        max_length=20,
        required=False
    )

    def clean(self):
        # run the standard clean method first
        super(buscar_por_nombreForm, self).clean()

        nombre = self.cleaned_data.get('nombre')
        apellido = self.cleaned_data.get('apellido')

        if not nombre:
            if not apellido:
                raise forms.ValidationError('Debe rellenar alguno de los dos')
        if not apellido:
            if not nombre:
                raise forms.ValidationError('Debe rellenar alguno de los dos')

        # always return the cleaned data
        return self.cleaned_data
