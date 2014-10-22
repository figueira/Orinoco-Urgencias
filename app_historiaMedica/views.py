# -*- encoding: utf-8 -*-
# coding: latin1

# Manejo de Sesion
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Formularios
from django.core.context_processors import csrf
from django.template import RequestContext

# General HTML
from django.shortcuts import render_to_response, redirect,\
    get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect

# Manejo de Informacion de esta aplicacion
from django.utils.timezone import utc
from datetime import datetime, date, timedelta
from app_emergencia.models import *
from app_emergencia.forms import *
from app_usuario.forms import *
from app_usuario.models import *

# Estadisticas
from django.db.models import Count

# JSON
from django.core import serializers
import json

# Expresiones regulares
import re

# Cuestiones de manejo de la base de datos
from django.db import transaction

#####################################################
# Imports Atencion
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from reportlab.platypus.flowables import *
from reportlab.lib.colors import pink, black, red, lightblue, white

import cgi
import json
from django.template.loader import render_to_string
from app_enfermedad.models import *
from app_paciente.models import *
from itertools import izip
from app_emergencia.pdf import *
# ###############


#########################################################
#                                                       #
#          Views para Casos de Uso de Atencion          #
#                                                       #
#########################################################

# A cada una le paso el id de emergencia para mantener la
# informacion constante en el sidebar izquierdo


def emergencia_descarga(request, id_emergencia, tipo_doc):

    emer = get_object_or_404(Emergencia, id=id_emergencia)
    ingreso = datetime.now()
    atList = Atencion.objects.filter(emergencia=id_emergencia)
    triage = Triage.objects.filter(emergencia=id_emergencia)
    atList2 = atList[:1]
    diags = Diagnostico.objects.filter(atencion=atList2)
    medicamento = Asignar.objects.filter(
        emergencia=id_emergencia, indicacion__tipo="medicamento")

    if tipo_doc == 'historia':
        return historia_med_pdf(request, id_emergencia)
    elif tipo_doc == 'constancia':
        return constancia_pdf(request, id_emergencia)
    elif tipo_doc == 'reportInd':
        return indicaciones_pdf(request, id_emergencia)
    elif tipo_doc == 'triage':
        return reporte_triage_pdf(request, id_emergencia)


@login_required(login_url='/')
def emergencia_enfermedad_actual(request, id_emergencia):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    paci = Paciente.objects.filter(emergencia__id=id_emergencia)
    paci = paci[0]
    triage = Triage.objects.filter(
        emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    mensaje = ""
    ya = ""
    atList = Atencion.objects.filter(emergencia=id_emergencia)

    # if len(atList) == 0:
    #     atencion = Atencion(
    #          emergencia=emer,medico=emer.responsable,fecha=datetime.now(),
    # fechaReal=datetime.now(),area_atencion=triage.areaAtencion)
    #     atencion.save()
    #     atList = Atencion.objects.filter(emergencia=id_emergencia)

    if request.method == 'POST':
        form = AgregarEnfActual(request.POST)
        if form.is_valid():
            pcd = form.cleaned_data
            narrativa = pcd['narrativa']
            # Busco si ya existe una narrativa para esa indicacion
            enfA = EnfermedadActual.objects.filter(atencion=atList[0].id)
            # Si existe, la sobreescribo
            if enfA:
                enfA[0].narrativa = narrativa
                enfA[0].save()

            else:
                enfA = EnfermedadActual(
                    atencion=atList[0], narrativa=narrativa)
                enfA.save()
                # mensaje = " Agregado Exitosamente: "+enfA.narrativa
                mensaje = " Agregado Exitosamente "
                info = {
                    'form': form, 'emergencia': emer, 'triage': triage,
                    'mensaje': mensaje, 'ya': ya
                    }
                return render_to_response(
                    'atencion_enfA.html', info,
                    context_instance=RequestContext(request))

            # mensaje = "Actualizado Exitosamente: "+enfA[0].narrativa
            mensaje = "Actualizado Exitosamente "
            info = {
                'form': form, 'emergencia': emer,
                'triage': triage, 'mensaje': mensaje, 'ya': ya}
            return render_to_response(
                'atencion_enfA.html', info,
                context_instance=RequestContext(request))

    enfa = EnfermedadActual.objects.filter(atencion=atList[0])

    if enfa:
        mensaje = "Ya se ha establecido una narrativa para este paciente"
        form = AgregarEnfActual(
            initial={'narrativa': enfa[0].narrativa})
        ya = "si"
    else:
        form = AgregarEnfActual()

    info = {
        'form': form,
        'emergencia': emer,
        'triage': triage,
        'mensaje': mensaje,
        'ya': ya
    }
    return render_to_response(
        'atencion_enfA.html',
        info,
        context_instance=RequestContext(request))

# --- RGV


@login_required(login_url='/')
def emergencia_atencion(request, id_emergencia, tipo):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    triage = Triage.objects.filter(
        emergencia=id_emergencia).order_by("-fechaReal")

    if len(triage) != 0:
        triage = triage[0]
        paci = Paciente.objects.filter(emergencia__id=id_emergencia)
        paci = paci[0]
        atList = Atencion.objects.filter(emergencia=id_emergencia)

        if len(atList) == 0:
            atencion = Atencion(
                emergencia=emer,
                medico=emer.responsable,
                fecha=datetime.now(),
                fechaReal=datetime.now(),
                area_atencion=triage.areaAtencion_id
            )
            atencion.save()
            atList = Atencion.objects.filter(emergencia=id_emergencia)

        if tipo == "listado":
            return redirect('/emergencia/listar/atencion')

        elif tipo == "historia":
            # Operaciones para determinar
            # si se muestran los botones de descarga
            historia_medica = False
            constancia = False
            indicaciones = False

            if len(atList) > 0:
                diags = Diagnostico.objects.filter(atencion=atList)
                enfA = EnfermedadActual.objects.filter(atencion=atList)
                indic = Asignar.objects.filter(emergencia=id_emergencia)

            if len(enfA) > 0 and len(diags) > 0:
                historia_medica = True

            if len(diags) > 0:
                constancia = True

            if len(indic) > 0:
                indicaciones = True

        ctx = {
            'emergencia': emer,
            'triage': triage,
            'hm_habilitado': historia_medica,
            'const_habilitado': constancia,
            'ind_habilitado': indicaciones
        }
        return render_to_response(
            'atencion.html',
            ctx,
            context_instance=RequestContext(request))


def emergencia_antecedentes_agregar(request, id_emergencia, tipo_ant):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    paci = Paciente.objects.get(emergencia__id=id_emergencia)
    triage = Triage.objects.filter(
        emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    vacio = ""

    if request.method == 'POST':
        nombres = request.POST.getlist('nuevoNombre')
        fechas = request.POST.getlist('nuevoFecha')
        atributo = request.POST.getlist('nuevoAtributo3')
        for i in range(len(nombres)-1):
            ant = Antecedente(tipo=tipo_ant, nombre=nombres[i])
            ant.save()
            pertenece = Pertenencia(paciente=paci, antecedente=ant)
            pertenece.save()
            if tipo_ant == 'medica' or tipo_ant == 'quirurgica':
                dia, mes, ano = fechas[i].split("/")
                fechaF = ano + "-" + mes + "-" + dia
                fecha = Fecha(fecha=fechaF, pertenencia=pertenece)
                fecha.save()
                if tipo_ant == 'medica':
                    tratamiento = Tratamiento(nombre=atributo[i])
                    tratamiento.save()
                    trataPerte = TratamientoPertenencia(
                        pertenencia=pertenece, tratamiento=tratamiento
                    )
                    trataPerte.save()
                if tipo_ant == 'quirurgica':
                    lugar = Lugar(nombre=atributo[i])
                    lugar.save()
                    lugarperte = LugarPertenencia(
                        lugar=lugar,
                        pertenencia=pertenece
                    )
                    lugarperte.save()

    antecedentes = Antecedente.objects.filter(
        pertenencia__paciente=paci, tipo=tipo_ant)

    if antecedentes:
        vacio = "no"

    pertenece = Pertenencia.objects.filter(
        paciente=paci,
        antecedente__tipo=tipo_ant
    )
    ctx = {
        'emergencia': emer,
        'triage': triage,
        'pertenece': pertenece,
        'tipo_ant': tipo_ant,
        'vacio': vacio}
    return render_to_response(
        'atencion_ant_medica.html',
        ctx,
        context_instance=RequestContext(request))


def emergencia_antecedentes_modificar(request, id_emergencia, tipo_ant):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    paci = Paciente.objects.get(emergencia__id=id_emergencia)
    triage = Triage.objects.filter(
        emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]

    antecedentes = Antecedente.objects.filter(
        pertenencia__paciente=paci, tipo=tipo_ant)
    for ant in antecedentes:
        ant.nombre = request.POST[str(ant.id)+"nombre"]
        if tipo_ant == 'medica' or tipo_ant == 'quirurgica':
            pertenece = Pertenencia.objects.filter(
                paciente=paci, antecedente=ant)
            if pertenece:
                fecha = Fecha.objects.get(pertenencia=pertenece[0])
                dia, mes, ano = request.POST[str(ant.id)+"fecha"].split("/")
                fecha.fecha = ano + "-" + mes + "-" + dia
                fecha.pertenencia = pertenece[0]
                fecha.save()
            if tipo_ant == 'medica':
                tratamiento = Tratamiento.objects.filter(
                    tratamientopertenencia__pertenencia=pertenece[0])
                if tratamiento:
                    tratamiento[0].nombre = request.POST[
                        str(ant.id)+"atributo3"]
                    tratamiento[0].save()
            if tipo_ant == 'quirurgica':
                lugar = Lugar.objects.filter(
                    lugarpertenencia__pertenencia=pertenece[0])
                if lugar:
                    lugar[0].nombre = request.POST[str(ant.id)+"atributo3"]
                    lugar[0].save()
        ant.save()

    if antecedentes:
        vacio = "no"

    pertenece = Pertenencia.objects.filter(
        paciente=paci,
        antecedente__tipo=tipo_ant
    )
    ctx = {
        'emergencia': emer,
        'triage': triage,
        'pertenece': pertenece,
        'tipo_ant': tipo_ant,
        'vacio': vacio
    }
    return render_to_response(
        'atencion_ant_medica.html',
        ctx,
        context_instance=RequestContext(request))


def emergencia_antecedentes_eliminar(request, id_emergencia, tipo_ant):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    paci = Paciente.objects.get(emergencia__id=id_emergencia)
    triage = Triage.objects.filter(
        emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]

    if request.method == 'POST':
        checkes = request.POST.getlist(u'check')
        for id_ant in checkes:
            ant = Antecedente(id=id_ant)
            pertenece = Pertenencia.objects.filter(
                paciente=paci, antecedente_id=id_ant)
            if pertenece:
                fecha = Fecha.objects.filter(
                    pertenencia=pertenece[0])
                fecha.delete()
                lugarpertence = LugarPertenencia.objects.filter(
                    pertenencia=pertenece[0])
                if lugarpertence:
                    lugar = Lugar.objects.filter(id=lugarpertence)
                    if lugar:
                        lugar.delete()
                    lugarpertence.delete()
                tratamientoPert = TratamientoPertenencia.objects.filter(
                    pertenencia=pertenece[0])
                if tratamientoPert:
                    tratamiento = Tratamiento.objects.filter(
                        id=tratamientoPert)
                    if tratamiento:
                        tratamiento.delete()
                    tratamientoPert.delete()
            pertenece.delete()
            ant.delete()

    antecedentes = Antecedente.objects.filter(
        pertenencia__paciente=paci, tipo=tipo_ant)
    if antecedentes:
        vacio = "no"

    pertenece = Pertenencia.objects.filter(
        paciente=paci, antecedente__tipo=tipo_ant)
    ctx = {
        'emergencia': emer,
        'triage': triage,
        'pertenece': pertenece,
        'tipo_ant': tipo_ant,
        'vacio': vacio
    }
    return render_to_response(
        'atencion_ant_medica.html',
        ctx,
        context_instance=RequestContext(request))


# ---------Gestion de Antecedentes en area de Atencion


@login_required(login_url='/')
def emergencia_antecedentes(request, id_emergencia):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    triage = Triage.objects.filter(
        emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    ctx = {
        'emergencia': emer,
        'triage': triage
    }
    return render_to_response(
        'atencion_ant.html',
        ctx,
        context_instance=RequestContext(request))

# ---------Gestion de Antecedentes en area de Atencion


@login_required(login_url='/')
def emergencia_antecedentes_tipo(request, id_emergencia, tipo_ant):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    paci = Paciente.objects.get(emergencia__id=id_emergencia)
    triage = Triage.objects.filter(
        emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    vacio = ""
    pertenece = Pertenencia.objects.filter(
        paciente=paci, antecedente__tipo=tipo_ant)
    antecedentes = Antecedente.objects.filter(
        pertenencia__paciente=paci, tipo=tipo_ant)

    if antecedentes:
        vacio = "no"

    ctx = {
        'emergencia': emer,
        'triage': triage,
        'antecedentes': antecedentes,
        'pertenece': pertenece,
        'tipo_ant': tipo_ant,
        'vacio': vacio}
    return render_to_response(
        'atencion_ant_medica.html',
        ctx,
        context_instance=RequestContext(request))


# -----------------------Gestion de Enfermedad (Examen Fisico)
@login_required(login_url='/')
def emergencia_enfermedad(request, id_emergencia):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    paci = Paciente.objects.get(emergencia__id=id_emergencia)
    triage = Triage.objects.filter(
        emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    causa = 0
    atencion = Atencion.objects.filter(emergencia=id_emergencia)
    aspectos = Aspecto.objects.filter(
        parteaspecto__partecuerpo__nombre='CABEZA Y ROSTRO')
    aspectoAten = AspectoAtencion.objects.filter(
        atencion=atencion[0],
        aspecto__parteaspecto__partecuerpo__nombre='CABEZA Y ROSTRO')
    ctx = {
        'emergencia': emer,
        'triage': triage,
        'causa': causa
    }
    if paci.sexo == 1:
        return render_to_response(
            'atencion_Plan.html',
            ctx,
            context_instance=RequestContext(request))
    else:
        return render_to_response(
            'atencion_Plan_mujer.html',
            ctx,
            context_instance=RequestContext(request))


@login_required(login_url='/')
def emergencia_enfermedad_zonacuerpo(request, id_emergencia, zona_cuerpo):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    paci = Paciente.objects.get(emergencia__id=id_emergencia)
    triage = Triage.objects.filter(
        emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    causa = 0
    atencion = Atencion.objects.filter(emergencia=id_emergencia)
    partecuerpo = ParteCuerpo.objects.filter(
        zonaparte__zonacuerpo__nombre=zona_cuerpo)
    parteaspecto = ParteAspecto.objects.filter(
        partecuerpo__zonaparte__zonacuerpo__nombre=zona_cuerpo)
    aspectoAten = AspectoAtencion.objects.filter(
        atencion=atencion[0],
        aspecto__parteaspecto__partecuerpo__zonaparte__zonacuerpo__nombre=zona_cuerpo)
    aspectos = Aspecto.objects.filter(
        parteaspecto__partecuerpo__zonaparte__zonacuerpo__nombre=zona_cuerpo)
    ctx = {
        'emergencia': emer,
        'triage': triage,
        'causa': causa,
        'paciente': paci,
        'partecuerpo': partecuerpo,
        'parteaspecto': parteaspecto,
        'aspectoAtencion': aspectoAten,
        'zona_cuerpo': zona_cuerpo
    }
    return render_to_response(
        'atencion_Plan_cuerpo.html',
        ctx,
        context_instance=RequestContext(request))


@login_required(login_url='/')
def emergencia_enfermedad_partecuerpo(request, id_emergencia, parte_cuerpo):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    triage = Triage.objects.filter(
        emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    causa = 0
    atencion = Atencion.objects.filter(emergencia=id_emergencia)
    atencion = atencion[0]
    aspectoAten = AspectoAtencion.objects.filter(
        atencion=atencion,
        aspecto__parteaspecto__partecuerpo__nombre=parte_cuerpo)
    aspectos = Aspecto.objects.filter(
        parteaspecto__partecuerpo__nombre=parte_cuerpo)
    if not(aspectoAten):
        for aspe in aspectos:
            AspeAten = AspectoAtencion(
                revisado='0',
                aspecto=aspe,
                atencion=atencion)
            AspeAten.save()
    aspectoAten = AspectoAtencion.objects.filter(
        atencion=atencion,
        aspecto__parteaspecto__partecuerpo__nombre=parte_cuerpo)
    ctx = {
        'emergencia': emer,
        'triage': triage,
        'causa': causa,
        'aspectoAtencion': aspectoAten,
        'parte_cuerpo': parte_cuerpo
    }
    return render_to_response(
        'atencion_Plan_partecuerpo.html',
        ctx,
        context_instance=RequestContext(request))


@login_required(login_url='/')
def emergencia_enfermedad_enviarcuerpo(request, id_emergencia, parte_cuerpo):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    triage = Triage.objects.filter(
        emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    causa = 0
    atencion = Atencion.objects.filter(emergencia=id_emergencia)
    atencion = atencion[0]
    aspectoAten = AspectoAtencion.objects.filter(
        atencion=atencion,
        aspecto__parteaspecto__partecuerpo__nombre=parte_cuerpo)
    partecuerpo = 0
    for aspAten in aspectoAten:
        input1 = request.POST[str(aspAten.aspecto.id)]
        if input1 == 'normal':
            aspAten.revisado = '1'
            anomalia = Anomalia.objects.filter(aspectoatencion=aspAten)
            if anomalia:
                anomalia.delete()
            aspAten.save()
        elif input1 == 'anormal':
            aspAten.revisado = '1'
            anomalia = Anomalia.objects.filter(aspectoatencion=aspAten)
            descripcion = request.POST['A'+str(aspAten.aspecto.id)]
            if anomalia:
                anomalia.descripcion = descripcion
                anomalia.save()
            else:
                anomalia = Anomalia(
                    descripcion=descripcion, aspectoatencion=aspAten)
                anomalia.save()
            aspAten.save()
        elif input1 == 'no':
            aspAten.revisado = '0'
            anomalia = Anomalia.objects.filter(aspectoatencion=aspAten)
            if anomalia:
                anomalia.delete()
            aspAten.save()

    return HttpResponse()
# --- RGV

# ----------------------------Gestion de INDICACIONES


@login_required(login_url='/')
def emergencia_indicaciones_ini(request, id_emergencia):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    paci = Paciente.objects.filter(emergencia__id=id_emergencia)
    paci = paci[0]
    triage = Triage.objects.filter(
        emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    ingreso = datetime.now()
    indicaciones = Indicacion.objects.filter(
        asignar__emergencia=id_emergencia)
    info = {
        'emergencia': emer,
        'triage': triage,
        'indicaciones': indicaciones,
        'ingreso': ingreso
    }
    return render_to_response(
        'atencion_ind.html',
        info,
        context_instance=RequestContext(request))


# Agrega las indicaciones dependiendo de la categoria:
@login_required(login_url='/')
def emergencia_indicaciones(request, id_emergencia, tipo_ind):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    paci = Paciente.objects.filter(emergencia__id=id_emergencia)
    paci = paci[0]
    triage = Triage.objects.filter(
        emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    ingreso = datetime.now()
    mensaje = ""
    ya = ""
    # ------------- Gestion de indicaciones con interfaz de tabla
    if tipo_ind == 'listar':
        indicaciones = Asignar.objects.filter(
            emergencia=id_emergencia, status=0)
        # print "Indicacion tipo en listar: ",indicaciones[0].indicacion.tipo
        # ed = EspDieta.objects.filter()
        info = {
            'mensaje': mensaje,
            'emergencia': emer,
            'triage': triage,
            'indicaciones': indicaciones
            }
        return render_to_response(
            'atencion_ind_listar.html',
            info,
            context_instance=RequestContext(request))

    elif tipo_ind == 'medicamento':
        indicaciones = Asignar.objects.filter(
            emergencia=id_emergencia,
            indicacion__tipo=tipo_ind,
            status=0)
        info = {
            'emergencia': emer,
            'triage': triage,
            'indicaciones': indicaciones,
            'tipo_ind': tipo_ind
        }
        return render_to_response(
            'atencion_ind_medica.html',
            info,
            context_instance=RequestContext(request))

    elif (
        tipo_ind == 'valora'
        or tipo_ind == 'otros'
        or tipo_ind == 'terapeutico'
        or tipo_ind == 'otras'
    ):
        indicaciones = Asignar.objects.filter(
            emergencia=id_emergencia,
            indicacion__tipo=tipo_ind,
            status=0)
        info = {
            'emergencia': emer,
            'triage': triage,
            'indicaciones': indicaciones,
            'tipo_ind': tipo_ind}
        return render_to_response(
            'atencion_ind_tera.html',
            info,
            context_instance=RequestContext(request))

    # ----- Gestion de indicaciones con interfaz de forms de Django
    else:
        indicaciones = Asignar.objects.filter(
            emergencia=id_emergencia, status=0)
        # indicaciones = Asignar.objects.filter(emergencia = id_emergencia)
        if request.method == 'POST':
            if tipo_ind == 'dieta':
                print "estoy en post de dieta"
                form = AgregarIndDietaForm(request.POST)

            elif tipo_ind == 'hidrata':
                form = AgregarIndHidrataForm(request.POST)

            elif tipo_ind == 'lab':
                form = AgregarIndLabForm(request.POST)

            elif tipo_ind == 'imagen':
                form = AgregarIndImgForm(request.POST)

            elif tipo_ind == 'endoscopico':
                form = AgregarIndEndosForm(request.POST)

            if form.is_valid():
                pcd = form.cleaned_data
                nombre = pcd[tipo_ind]
                print "Imprime lo que me retorna el form %s: " % \
                    (tipo_ind), nombre
                print "nombreeee %s" % tipo_ind
                print request.POST

                # Condicional para validar/agregar
                # indicaciones de tipo lab/endoscopicos:
                if tipo_ind == 'lab' or tipo_ind == 'endoscopico':
                    agregado = False
                    modificado = False
                    # Es multichoice entonces hago un for por todas las
                    # opciones elegidas
                    for i in range(len(nombre)):
                        indicacionesQ = Indicacion.objects.filter(
                            asignar__emergencia=id_emergencia,
                            asignar__indicacion__nombre=nombre[i])
                        if indicacionesQ:
                            modificado = True
                        else:
                            indicaciones = Asignar.objects.filter(
                                emergencia=id_emergencia, status=0)
                            # indicaciones = Asignar.objects.filter(
                            # emergencia = id_emergencia)
                            i = Indicacion.objects.get(nombre=nombre[i])
                            a = Asignar(
                                emergencia=emer,
                                indicacion=i,
                                persona=emer.responsable,
                                fecha=datetime.now(),
                                fechaReal=datetime.now(),
                                status=0)
                            a.save()
                            agregado = True

                    if tipo_ind == 'endoscopico':
                        if request.POST.get('c_214', False):
                            i = Indicacion.objects.get(nombre="Arterografia")
                            asig = Asignar(
                                emergencia=emer,
                                indicacion=i,
                                persona=emer.responsable,
                                fecha=datetime.now(),
                                fechaReal=datetime.now(),
                                status=0)
                            asig.save()
                            p_cuerpo = request.POST['c_214']
                            ex = EspImg(asignacion=asig, parte_cuerpo=p_cuerpo)
                            ex.save()
                            agregado = True
                        if request.POST.get('c_215', False):
                            i = Indicacion.objects.get(nombre="Otros")
                            asig = Asignar(
                                emergencia=emer,
                                indicacion=i,
                                persona=emer.responsable,
                                fecha=datetime.now(),
                                fechaReal=datetime.now(),
                                status=0)
                            asig.save()
                            p_cuerpo = request.POST['c_215']
                            ex = EspImg(
                                asignacion=asig,
                                parte_cuerpo=p_cuerpo)
                            ex.save()
                            agregado = True

                    print tipo_ind
                    print agregado
                    if tipo_ind == 'lab' and agregado:
                        espe = get_object_or_404(
                            Espera, nombre='Laboratorio')
                        espera_lab = EsperaEmergencia.objects.filter(
                            emergencia=id_emergencia,
                            espera=espe,
                            hora_fin=None)

                        # Se verifica que ya la causa
                        # de espera de lab no este agregada
                        if len(espera_lab) == 0:
                            espera1 = EsperaEmergencia(
                                espera=espe, emergencia=emer, estado='0')
                            espera1.save()

                    elif tipo_ind == 'endoscopico' and agregado:
                        espe = get_object_or_404(Espera, nombre='Estudios')
                        espera_est = EsperaEmergencia.objects.filter(
                            emergencia=id_emergencia,
                            espera=espe,
                            hora_fin=None)

                        # Se verifica que ya la causa de espera de
                        # estudio no este agregada
                        if len(espera_est) == 0:
                            espera1 = EsperaEmergencia(
                                espera=espe, emergencia=emer, estado='0')
                            espera1.save()

                    if modificado:
                        ya = "si"
                        mensaje = "Laboratorios Modificados Exitosamente"
                        info = {
                            'form': form,
                            'mensaje': mensaje,
                            'emergencia': emer,
                            'tipo_ind': tipo_ind,
                            'ya': ya
                        }
                        return render_to_response(
                            'atencion_ind_hidrata.html',
                            info,
                            context_instance=RequestContext(request))

                    mensaje = "Procedimientos Guardados Exitosamente"
                    info = {
                        'form': form,
                        'mensaje': mensaje,
                        'emergencia': emer,
                        'triage': triage,
                        'indicaciones': indicaciones,
                        'tipo_ind': tipo_ind
                    }
                    return render_to_response(
                        'atencion_ind_listar.html',
                        info,
                        context_instance=RequestContext(request))

                if tipo_ind == 'imagen':
                    agregado = False
                    modificado = False
                    for i in range(len(nombre)):
                        indicacionesQ = Indicacion.objects.filter(
                            asignar__emergencia=id_emergencia,
                            asignar__indicacion__nombre=nombre[i])
                        if indicacionesQ:
                            modificado = True
                        else:
                            indicaciones = Asignar.objects.filter(
                                emergencia=id_emergencia, status=0)
                            # indicaciones =
                            # Asignar.objects.filter(emergencia = id_emergencia
                            # )
                            i = Indicacion.objects.get(nombre=nombre[i])
                            a = Asignar(
                                emergencia=emer,
                                indicacion=i,
                                persona=emer.responsable,
                                fecha=datetime.now(),
                                fechaReal=datetime.now(),
                                status=0)
                            a.save()
                            p_cuerpo = request.POST["c_"+str(i.id)]
                            ex = EspImg(
                                asignacion=a,
                                parte_cuerpo=p_cuerpo)
                            ex.save()
                            agregado = True

                    if agregado:
                        espe = get_object_or_404(Espera, nombre='Imagenologia')
                        espera_img = EsperaEmergencia.objects.filter(
                            emergencia=id_emergencia,
                            espera=espe,
                            hora_fin=None)

                        # Se verifica que ya la causa de espera
                        # de imagenologia no este agregada
                        if len(espera_img) == 0:
                            espera1 = EsperaEmergencia(
                                espera=espe,
                                emergencia=emer,
                                estado='0')
                            espera1.save()

                    if modificado:
                        ya = "si"
                        mensaje = "Imagenologia Modificada Exitosamente"
                        info = {
                            'form': form,
                            'mensaje': mensaje,
                            'emergencia': emer,
                            'tipo_ind': tipo_ind,
                            'ya': ya}
                        return render_to_response(
                            'atencion_ind_hidrata.html',
                            info,
                            context_instance=RequestContext(request))

                    mensaje = "Procedimientos Guardados Exitosamente"
                    info = {
                        'form': form,
                        'mensaje': mensaje,
                        'emergencia': emer,
                        'triage': triage,
                        'indicaciones': indicaciones,
                        'tipo_ind': tipo_ind
                    }
                    return render_to_response(
                        'atencion_ind_listar.html',
                        info,
                        context_instance=RequestContext(request))

                # Condicional para validar/agregar
                # indicaciones de tipo dieta e hidratacion
                else:
                    # indicacionesQ = Indicacion.objects.filter
                    # (asignar__emergencia = id_emergencia,
                    # asignar__indicacion__nombre = nombre)
                    indicacionesQ = Indicacion.objects.filter(
                        asignar__emergencia=id_emergencia,
                        asignar__indicacion__tipo=tipo_ind)
                    if indicacionesQ:		# MODIFICAR DIETA E HIDTRACION
                        if tipo_ind == 'dieta':
                            a = Asignar.objects.filter(
                                emergencia=id_emergencia,
                                indicacion=indicacionesQ)
                            a = a[0]
                            d = EspDieta.objects.filter(asignacion=a)
                            d = d[0]
                            d.observacion = pcd['observacion']
                            d.save()
                            a.indicacion = Indicacion.objects.get(
                                nombre=nombre)
                            a.status = 0
                            a.save()
                        elif tipo_ind == 'hidrata':
                            a = Asignar.objects.filter(
                                emergencia=id_emergencia,
                                indicacion=indicacionesQ)
                            a = a[0]
                            h = EspHidrata.objects.filter(asignacion=a)
                            h = h[0]
                            h.volumen = pcd['volumen']
                            h.vel_infusion = pcd['vel_inf']
                            h.vel_inf_unidad = pcd['vel_inf_unidad']
                            h.complementos = pcd['complementos']
                            h.save()
                            a.indicacion = Indicacion.objects.get(
                                nombre=nombre)
                            a.status = 0
                            a.save()
                            comb = CombinarHidrata.objects.filter(
                                hidratacion1__asignacion__indicacion=indicacionesQ)
                            if pcd['combina'] == "True":
                                ex_sol = pcd['combina_sol']
                                i2 = Indicacion.objects.get(nombre=ex_sol)
                                if len(comb) > 0:
                                    comb = comb[0]
                                    comb.hidratacion2 = i2
                                    comb.save()
                                else:
                                    combi = CombinarHidrata(
                                        hidratacion1=h,
                                        hidratacion2=i2)
                                    combi.save()
                            else:
                                if len(comb) > 0:
                                    comb.delete()
                        ya = "si"
                        mensaje = "Indicacion Modificada Exitosamente"
                        info = {
                            'form': form,
                            'mensaje': mensaje,
                            'tipo_ind': tipo_ind,
                            'ya': ya,
                            'emergencia': emer}
                        return render_to_response(
                            'atencion_ind_hidrata.html',
                            info,
                            context_instance=RequestContext(request))

                    else:		# AGREGAR DIETA E HIDTRACION
                        indicaciones = Asignar.objects.filter(
                            emergencia=id_emergencia, status=0)
                        # indicaciones = Asignar.objects.filter
                        # (emergencia = id_emergencia)
                        i = Indicacion.objects.get(nombre=nombre)
                        a = Asignar(
                            emergencia=emer,
                            indicacion=i,
                            persona=emer.responsable,
                            fecha=datetime.now(),
                            fechaReal=datetime.now(),
                            status=0)
                        a.save()
                        if tipo_ind == 'dieta':
                            extra = pcd['observacion']
                            ex = EspDieta(
                                asignacion=a,
                                observacion=extra)
                            ex.save()
                        elif tipo_ind == 'hidrata':
                            sn = pcd['combina']
                            vol = pcd['volumen']
                            vel = pcd['vel_inf']
                            vel_uni = pcd['vel_inf_unidad']
                            comp = pcd['complementos']
                            ex = EspHidrata(
                                asignacion=a,
                                volumen=vol,
                                vel_infusion=vel,
                                vel_inf_unidad=vel_uni,
                                complementos=comp)
                            ex.save()
                            if pcd['combina'] == "True":
                                ex_sol = pcd['combina_sol']
                                i2 = Indicacion.objects.get(nombre=ex_sol)
                                comb = CombinarHidrata(
                                    hidratacion1=ex, hidratacion2=i2)
                                comb.save()
                        mensaje = "Procedimientos Guardado Exitosamente"
                        info = {
                            'form': form,
                            'mensaje': mensaje,
                            'emergencia': emer,
                            'triage': triage,
                            'indicaciones': indicaciones,
                            'tipo_ind': tipo_ind
                            }
                        return render_to_response(
                            'atencion_ind_listar.html',
                            info,
                            context_instance=RequestContext(request))
            else:
                form_errors = form.errors
                info = {
                    'form': form,
                    'mensaje': mensaje,
                    'tipo_ind': tipo_ind,
                    'form_errors': form_errors,
                    'emergencia': emer}
                return render_to_response(
                    'atencion_ind_hidrata.html',
                    info,
                    context_instance=RequestContext(request))

        # --------Renderizado de formularios al ingresar por primera vez-----#
        if tipo_ind == 'dieta':
            d = Asignar.objects.filter(
                emergencia=id_emergencia,
                indicacion__tipo="dieta")

            if d:
                e = EspDieta.objects.filter(asignacion=d[0])
                print "ver observacion: ", e[0].observacion
                print "ver dietas iniciales", d
                print "Nombre Inicial: ", d[0].indicacion.nombre
                form = AgregarIndDietaForm(
                    initial={
                        'dieta': d[0].indicacion.pk,
                        'observacion': e[0].observacion
                    }
                )
                mensaje = "Ya tiene agregadas las siguientes indicaciones"
                ya = "si"

            else:
                form = AgregarIndDietaForm()

        elif tipo_ind == 'hidrata':
            h = Asignar.objects.filter(
                emergencia=id_emergencia,
                indicacion__tipo="hidrata")
            if h:
                e = EspHidrata.objects.filter(asignacion=h[0])
                c = CombinarHidrata.objects.filter(hidratacion1=e[0])
                mensaje = "Ya tiene agregadas las siguientes indicaciones"
                ya = "si"
                if c:
                    form = AgregarIndHidrataForm(
                        initial={
                            'hidrata': h[0].indicacion.pk,
                            'combina': True,
                            'combina_sol': c[0].hidratacion2.pk,
                            'volumen': e[0].volumen,
                            'vel_inf': e[0].vel_infusion,
                            'vel_inf_unidad': e[0].vel_inf_unidad,
                            'complementos': e[0].complementos})
                else:
                    form = AgregarIndHidrataForm(
                        initial={
                            'hidrata': h[0].indicacion.pk,
                            'combina': False,
                            'volumen': e[0].volumen,
                            'vel_inf': e[0].vel_infusion,
                            'vel_inf_unidad': e[0].vel_inf_unidad,
                            'complementos': e[0].complementos})
            else:
                form = AgregarIndHidrataForm()

        elif tipo_ind == 'lab':
            labi = Asignar.objects.filter(
                emergencia=id_emergencia,
                indicacion__tipo="lab",
                status=0)
            if labi:
                lab_list = []
                for l in labi:
                    lab_list.append(l.indicacion.pk)

                form = AgregarIndLabForm(
                    initial={
                        'lab': lab_list
                        }
                )
                mensaje = "Ya tiene agregadas las siguientes indicaciones"
                ya = "si"
            else:
                form = AgregarIndLabForm()

        elif tipo_ind == 'imagen':
            img = Asignar.objects.filter(
                emergencia=id_emergencia,
                indicacion__tipo="imagen",
                status=0)
            if img:
                img_list = []
                for im in img:
                    img_list.append(im.indicacion.pk)

                form = AgregarIndImgForm(
                    initial={
                        'imagen': img_list
                    }
                )
                mensaje = "Ya tiene agregadas las siguientes indicaciones"
                ya = "si"
            else:
                form = AgregarIndImgForm()

        elif tipo_ind == 'endoscopico':
            end = Asignar.objects.filter(
                emergencia=id_emergencia,
                indicacion__tipo="endoscopico",
                status=0)
            if end:
                end_list = []
                for e in end:
                    end_list.append(e.indicacion.pk)

                form = AgregarIndEndosForm(
                    initial={
                        'endoscopico': end_list
                    }
                )
                mensaje = "Ya tiene agregadas las siguientes indicaciones"
                ya = "si"
            else:
                form = AgregarIndEndosForm()

        info = {
            'form': form,
            'mensaje': mensaje,
            'tipo_ind': tipo_ind,
            'ya': ya,
            'emergencia': emer}
        return render_to_response(
            'atencion_ind_hidrata.html',
            info,
            context_instance=RequestContext(request))


# -------------------------------Listar Info Extra
@login_required(login_url='/')
def emergencia_indicacion_info(request, id_asignacion, tipo_ind):
    extra2 = ""
    extra = ""
    if tipo_ind == "dieta":
        extra = EspDieta.objects.get(asignacion=id_asignacion)

    elif tipo_ind == "hidrata":
        extra = EspHidrata.objects.get(asignacion=id_asignacion)
        ver = CombinarHidrata.objects.filter(hidratacion1=extra)
        if ver:
            extra2 = ver[0]

    elif tipo_ind == "medicamento":
        extra = EspMedics.objects.get(asignacion=id_asignacion)
        ver = tieneSOS.objects.filter(espMed=extra)
        if ver:
            extra2 = ver[0]

    elif tipo_ind == "imagen":
        extra = EspImg.objects.get(asignacion=id_asignacion)

    elif tipo_ind == "endoscopico":
        extra = EspImg.objects.get(asignacion=id_asignacion)
        print "asignacion iddddd %s" % extra.asignacion_id
        asig = Asignar.objects.get(id=extra.asignacion_id)
        final = Indicacion.objects.get(id=asig.indicacion_id)
        print "finaaaaal %s" % final.nombre
        extra2 = final.nombre

    info = {
        'tipo_ind': tipo_ind,
        'extra': extra,
        'extra2': extra2
    }
    return render_to_response(
        'atencion_ind_listExtra.html',
        info,
        context_instance=RequestContext(request))


# ---Acciones CRUD
# ---AGREGAR
@login_required(login_url='/')
def emergencia_indicaciones_agregar(request, id_emergencia, tipo_ind):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    paci = Paciente.objects.filter(emergencia__id=id_emergencia)
    paci = paci[0]
    triage = Triage.objects.filter(
        emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    mensaje = ""
    atencion = Atencion.objects.filter(emergencia=emer)

    if request.method == 'POST':
        if tipo_ind == 'diagnostico':
            diags = Diagnostico.objects.filter(atencion=atencion[0])
            diagnostico = request.POST.getlist('nuevoDiag')
            # Consulta diagnosticos:
            ver = range(len(diagnostico)-1)
            for i in ver:
                # Condicional para saber si existen los diagnosticos:
                enfermedad = Enfermedad.objects.get(id=diagnostico[i])
                diagnosticoQ = Diagnostico.objects.filter(
                    atencion=atencion[0],
                    enfermedad=enfermedad
                )
                if diagnosticoQ:
                    mensaje = "Hay Diagnosticos con este nombre: " +\
                        diagnosticoQ[0].enfermedad.descripcion
                    info = {
                        'mensaje': mensaje,
                        'emergencia': emer,
                        'triage': triage,
                        'tipo_ind': tipo_ind,
                        'diags': diags
                    }
                    return render_to_response(
                        'atencion_diag.html',
                        info,
                        context_instance=RequestContext(request))
                else:
                    diag = Diagnostico(
                        atencion=atencion[0], enfermedad=enfermedad)
                    diag.save()
            mensaje = "Diagnosticos guardados Exitosamente"
            info = {
                'mensaje': mensaje,
                'emergencia': emer,
                'triage': triage,
                'tipo_ind': tipo_ind,
                'diags': diags
            }
            return render_to_response(
                'atencion_diag.html',
                info,
                context_instance=RequestContext(request))

        elif (
            tipo_ind == 'valora'
            or tipo_ind == 'otros'
            or tipo_ind == 'terapeutico'
            or tipo_ind == 'otras'
        ):
            indicaciones = Asignar.objects.filter(
                emergencia=id_emergencia, indicacion__tipo=tipo_ind)
            nombres = request.POST.getlist('nuevaInd')
            ver = range(len(nombres)-1)
            for i in ver:
                # Condicional para saber si existe en las indicaciones:
                indicacionesQ = Indicacion.objects.filter(
                    asignar__emergencia=id_emergencia,
                    asignar__indicacion__nombre=nombres[i])
                if indicacionesQ:
                    mensaje = "Hay indicaciones con este nombre: " +\
                        indicacionesQ[0].nombre
                    info = {
                        'mensaje': mensaje,
                        'emergencia': emer,
                        'triage': triage,
                        'indicaciones': indicaciones,
                        'tipo_ind': tipo_ind
                    }
                    return render_to_response(
                        'atencion_ind_tera.html',
                        info,
                        context_instance=RequestContext(request))
                else:
                    # Creo el objeto indicacion
                    ind = Indicacion(nombre=nombres[i], tipo=tipo_ind)
                    ind.save()
                    a = Asignar(
                        emergencia=emer,
                        indicacion=ind,
                        persona=emer.responsable,
                        fecha=datetime.now(),
                        fechaReal=datetime.now(),
                        status=0)
                    a.save()
            mensaje = "Indicaciones guardadas Exitosamente"
            info = {
                'mensaje': mensaje,
                'emergencia': emer,
                'triage': triage,
                'indicaciones': indicaciones,
                'tipo_ind': tipo_ind
            }
            return render_to_response(
                'atencion_ind_tera.html',
                info,
                context_instance=RequestContext(request))

        elif tipo_ind == 'medicamento':
            indicaciones = Asignar.objects.filter(
                emergencia=id_emergencia,
                indicacion__tipo=tipo_ind
            )
            nombres = request.POST.getlist('nuevaMed')
            dosis = request.POST.getlist('nuevaDosis')
            tc = request.POST.getlist('nuevoTC')
            frec = request.POST.getlist('nuevaFrec')
            via = request.POST.getlist('nuevaVAD')
            tf = request.POST.getlist('nuevoTF')
            situacion = request.POST.getlist('situacion')
            comentario = request.POST.getlist('comentario')
            ver = range(len(nombres)-1)
            print "nombres", nombres
            print "Situacion", situacion
            print "Comentarios", comentario
            print "verr rango: "+str(ver)
            for i in ver:
                # Condicional para saber si existe en las indicaciones:
                indicacionesQ = Indicacion.objects.filter(
                    asignar__emergencia=id_emergencia,
                    asignar__indicacion__nombre=nombres[i])
                if indicacionesQ:
                    mensaje = "Hay indicaciones con este nombre: " +\
                        indicacionesQ[0].nombre
                    info = {
                        'mensaje': mensaje,
                        'emergencia': emer,
                        'triage': triage,
                        'indicaciones': indicaciones,
                        'tipo_ind': tipo_ind
                    }
                    return render_to_response(
                        'atencion_ind_medica.html',
                        info,
                        context_instance=RequestContext(request))
                else:
                    # Creo el objeto indicacion
                    print "nombre: ", nombres[i]
                    ind = Indicacion(nombre=nombres[i], tipo=tipo_ind)
                    ind.save()
                    a = Asignar(
                        emergencia=emer,
                        indicacion=ind,
                        persona=emer.responsable,
                        fecha=datetime.now(),
                        fechaReal=datetime.now(),
                        status=0
                    )
                    a.save()
                    # Agregar info extra:
                    eMed = EspMedics(
                        asignacion=a,
                        dosis=float(dosis[i]),
                        tipo_conc=tc[i],
                        frecuencia=frec[i],
                        tipo_frec=tf[i],
                        via_admin=via[i])
                    eMed.save()
                    print "Objeto guardado numero: "+str(i)+"\n"
                    print eMed.asignacion.indicacion.nombre
                    if tf[i] == "sos":
                        print "situaciones = ", situacion
                        print "comentarios = ", comentario
                        print "situaciones numero: "+str(i)+"\n"
                        print situacion[i]
                        print "comentarios numero: "+str(i)+"\n"
                        print comentario[i]
                        tSos = tieneSOS(
                            espMed=eMed,
                            situacion=situacion[i],
                            comentario=comentario[i])
                        tSos.save()

            mensaje = "Medicaciones guardadas Exitosamente"
            info = {
                'mensaje': mensaje,
                'emergencia': emer,
                'triage': triage,
                'indicaciones': indicaciones,
                'tipo_ind': tipo_ind}
            return render_to_response(
                'atencion_ind_medica.html',
                info,
                context_instance=RequestContext(request))
    else:
        mensaje = "ELSE PORQ NO HAY POST"
        info = {
            'mensaje': mensaje,
            'emergencia': emer,
            'triage': triage,
            'indicaciones': indicaciones,
            'tipo_ind': tipo_ind
        }
        return render_to_response(
            'atencion_ind_medica.html',
            info,
            context_instance=RequestContext(request))


# ---------------------------ELIMINAR
@login_required(login_url='/')
def emergencia_indicaciones_eliminar(request, id_emergencia, tipo_ind):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    paci = Paciente.objects.filter(emergencia__id=id_emergencia)
    paci = paci[0]
    triage = Triage.objects.filter(
        emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    mensaje = ""
    atencion = Atencion.objects.filter(emergencia=emer)

    if request.method == 'POST':
        checkes = request.POST.getlist(u'check')

        if tipo_ind == "diagnostico":
            # obj tiene el id de la relacion
            for obj in checkes:
                relDiag = Diagnostico.objects.get(id=obj)
                # Borro ese objeto:
                relDiag.delete()
                diags = Diagnostico.objects.filter(atencion=atencion[0])
            mensaje = "Diagnosticos eliminado Exitosamente"
            info = {
                'mensaje': mensaje,
                'emergencia': emer,
                'triage': triage,
                'tipo_ind': tipo_ind,
                'diags': diags
            }
            return render_to_response(
                'atencion_diag.html',
                info,
                context_instance=RequestContext(request))

        elif tipo_ind == "dieta":
            indicacionesQ = Indicacion.objects.filter(
                asignar__emergencia=id_emergencia,
                asignar__indicacion__tipo=tipo_ind)
            a = Asignar.objects.filter(
                emergencia=id_emergencia,
                indicacion=indicacionesQ)
            d = EspDieta.objects.filter(asignacion=a)
            d.delete()
            a.delete()
            ya = ""
            mensaje = "Indicacion Eliminada Exitosamente"
            form = AgregarIndDietaForm()
            info = {
                'form': form,
                'mensaje': mensaje,
                'tipo_ind': tipo_ind,
                'ya': ya,
                'emergencia': emer
            }
            return render_to_response(
                'atencion_ind_hidrata.html',
                info,
                context_instance=RequestContext(request))

        elif tipo_ind == "hidrata":
            indicacionesQ = Indicacion.objects.filter(
                asignar__emergencia=id_emergencia,
                asignar__indicacion__tipo=tipo_ind)
            a = Asignar.objects.filter(
                emergencia=id_emergencia,
                indicacion=indicacionesQ)
            h = EspHidrata.objects.filter(asignacion=a)
            h.delete()
            a.delete()
            comb = CombinarHidrata.objects.filter(
                hidratacion1__asignacion__indicacion=indicacionesQ)
            if len(comb) > 0:
                comb.delete()
            ya = ""
            mensaje = "Indicacion Eliminada Exitosamente"
            form = AgregarIndHidrataForm()
            info = {
                'form': form,
                'mensaje': mensaje,
                'tipo_ind': tipo_ind,
                'ya': ya,
                'emergencia': emer}
            return render_to_response(
                'atencion_ind_hidrata.html',
                info,
                context_instance=RequestContext(request))

        elif tipo_ind == "normal":
            for obj in checkes:
                asig = Asignar.objects.get(id=obj)
                tipo = asig.indicacion.tipo
                asig.fecha = datetime.now()
                asig.fechaReal = datetime.now()
                print "ASIG object: ", asig

                asig.status = 1
                asig.save()

            indicaciones = Asignar.objects.filter(
                emergencia=id_emergencia, status=0)
            mensaje = "Cambio de status realizado Exitosamente"
            info = {
                'mensaje': mensaje,
                'emergencia': emer,
                'triage': triage,
                'indicaciones': indicaciones,
                'tipo_ind': tipo_ind
            }
            return render_to_response(
                'atencion_ind_listar.html',
                info,
                context_instance=RequestContext(request))


# ---------------------MODIFICAR
def emergencia_indicaciones_modificar(request, id_emergencia, tipo_ind):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    paci = Paciente.objects.filter(emergencia__id=id_emergencia)
    paci = paci[0]
    triage = Triage.objects.filter(
        emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    mensaje = ""

    if tipo_ind == "diagnostico":
        at = Atencion.objects.filter(emergencia=id_emergencia)
        diags = Diagnostico.objects.filter(atencion=at[0])
        for d in diags:
            enfermedad = Enfermedad.objects.get(
                id=request.POST[str(d.id)+"nombre"])
            d.enfermedad = enfermedad
            d.save()

        mensaje = " Modificado Exitosamente "
        info = {
            'mensaje': mensaje,
            'emergencia': emer,
            'diags': diags,
            'tipo_ind': tipo_ind}
        return render_to_response(
            'atencion_diag.html',
            info,
            context_instance=RequestContext(request))

    elif (
        tipo_ind == 'valora'
        or tipo_ind == 'otros'
        or tipo_ind == 'terapeutico'
    ):
        indicaciones = Asignar.objects.filter(
            emergencia=id_emergencia, indicacion__tipo=tipo_ind)
        for ia in indicaciones:
            # No verifica si nombre ya existe:
            ia.indicacion.nombre = request.POST[str(ia.id)+"nombre"]
            i = Indicacion.objects.get(id=ia.indicacion.id)
            i.nombre = request.POST[str(ia.id)+"nombre"]
            i.fecha = datetime.now()
            i.fechaReal = datetime.now()
            i.save()
            ia.save()
        indsN = Asignar.objects.filter(
            emergencia=id_emergencia,
            indicacion__tipo=tipo_ind)
        mensaje = " Modificado Exitosamente "
        info = {
            'mensaje': mensaje,
            'emergencia': emer,
            'indicaciones': indsN,
            'tipo_ind': tipo_ind
        }
        return render_to_response(
            'atencion_ind_tera.html',
            info,
            context_instance=RequestContext(request))

    elif tipo_ind == "medicamento":
        indicaciones = Asignar.objects.filter(
            emergencia=id_emergencia,
            indicacion__tipo=tipo_ind)
        for ind in indicaciones:
            ind.indicacion.nombre = request.POST[str(ind.id)+"nombre"]
            ii = Indicacion.objects.get(id=ind.indicacion.id)
            ii.nombre = request.POST[str(ind.id)+"nombre"]
            ii.fecha = datetime.now()
            ii.fechaReal = datetime.now()
            ii.save()
            ind.save()
            extraO = EspMedics.objects.get(asignacion=ind)
            extraO.dosis = request.POST[str(ind.id)+"dosis"]
            extraO.tipo_conc = request.POST[str(ind.id)+"conc"]
            extraO.frecuencia = request.POST[str(ind.id)+"frec"]
            # Falta agregar los inputs para modificar comentario y situacion:
            # extraO.tipo_frec = request.POST[str(ind.id)+"t_frec"]
            extraO.via_admin = request.POST[str(ind.id)+"via_adm"]
            extraO.save()

        indicaciones = Asignar.objects.filter(
            emergencia=id_emergencia, indicacion__tipo=tipo_ind)
        print "Pastillas asignadas", indicaciones
        mensaje = " Modificado Exitosamente"
        info = {
            'mensaje': mensaje,
            'emergencia': emer,
            'triage': triage,
            'indicaciones': indicaciones,
            'tipo_ind': tipo_ind
        }
        return render_to_response(
            'atencion_ind_medica.html',
            info,
            context_instance=RequestContext(request))


# ---------Gestion de Diagnostico Definitivo
@login_required(login_url='/')
def emergencia_diagnostico(request, id_emergencia):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    paci = Paciente.objects.filter(emergencia__id=id_emergencia)
    paci = paci[0]
    triage = Triage.objects.filter(
        emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[:1]
    tipo_ind = 'diagnostico'
    at = Atencion.objects.filter(emergencia=id_emergencia)
    diags = Diagnostico.objects.filter(atencion=at[0])
    mensaje = ""
    info = {
        'mensaje': mensaje,
        'emergencia': emer,
        'triage': triage,
        'diags': diags,
        'tipo_ind': tipo_ind
    }
    return render_to_response(
        'atencion_diag.html',
        info,
        context_instance=RequestContext(request))

# Funcion que recibe el formulario para evaluar a un paciente y lo procesa


@login_required(login_url='/')
def evaluar_paciente(request, id_emergencia):
    medico = Usuario.objects.get(username=request.user)
    # Si usuario es doctor o enfermero
    if ((medico.tipo == "1") or (medico.tipo == "2")):
        if request.method == 'POST':
            emergencia = get_object_or_404(Emergencia, id=id_emergencia)
            triage = Triage.objects.filter(emergencia=emergencia)
            form = FormularioEvaluacionPaciente(request.POST)
            es_valido = form.is_valid()

            if es_valido:
                fechaReal = datetime.now()
                motivo = Motivo.objects.get(nombre__startswith=" Ingreso")
                area = AreaEmergencia.objects.get(
                    nombre__startswith=" Ingreso")
                evaluacion = form.cleaned_data

                # Si no existe triage para esa emergencia crea uno
                if len(triage) == 0:
                    t = Triage(
                        emergencia=emergencia,
                        medico=medico,
                        fecha=fechaReal,
                        motivo=motivo,
                        areaAtencion=area,
                        signos_tmp=evaluacion['temperatura'],
                        signos_fc=evaluacion['frecuencia_cardiaca'],
                        signos_fr=evaluacion['frecuencia_respiratoria'],
                        signos_pa=evaluacion['presion_diastolica'],
                        signos_pb=evaluacion['presion_sistolica'],
                        signos_saod=evaluacion['saturacion_oxigeno'],
                        signos_avpu=evaluacion['avpu'],
                        signos_dolor=evaluacion['intensidad_dolor'])
                    t.save()
                # Si existe triage para esa emergencia lo actualiza
                else:
                    triage = triage[0]
                    triage.medico = medico
                    triage.fecha = fechaReal
                    triage.motivo = motivo
                    triage.areaAtencion = area
                    triage.signos_tmp = evaluacion['temperatura']
                    triage.signos_fc = evaluacion['frecuencia_cardiaca']
                    triage.signos_fr = evaluacion['frecuencia_respiratoria']
                    triage.signos_pa = evaluacion['presion_diastolica']
                    triage.signos_pb = evaluacion['presion_sistolica']
                    triage.signos_saod = evaluacion['saturacion_oxigeno']
                    triage.signos_avpu = evaluacion['avpu']
                    triage.signos_dolor = evaluacion['intensidad_dolor']
                    triage.save()

        csrf_token_value = request.COOKIES['csrftoken']
        plantilla_formulario = render_to_string(
            'formularios/evaluacionPaciente.html',
            {
                'idE': id_emergencia,
                'csrf_token_value': csrf_token_value,
                'form': form
            }
        )
        return render(
            request,
            'scripts/evaluacionPaciente.js',
            {
                'es_valido': es_valido,
                'id_emergencia': id_emergencia,
                'plantilla_formulario': plantilla_formulario
            },
            content_type='text/javascript')

    return redirect("/")


def agregarEnfermedad(request, nombre_enfermedad):

    string = nombre_enfermedad
    Sugerencias = serializers.serialize(
        "json", Enfermedad.objects.filter(
            descripcion__icontains=string)[:5])
    return HttpResponse(
        json.dumps(Sugerencias),
        content_type='application/json')


@login_required(login_url='/')
def paciente_perfil_emergencia(request, idE):
    ea = get_object_or_404(Emergencia, pk=idE)
    p = get_object_or_404(Paciente, pk=ea.paciente.id)
    t = Triage.objects.filter(emergencia=ea)
    historia_medica = False
    constancia = False
    indicaciones = False
    if len(t) != 0:
        t = t[0]
        atList = Atencion.objects.filter(emergencia=idE)
        # Operaciones para determinar si se muestran los botones de descarga
        if len(atList) > 0:
            diags = Diagnostico.objects.filter(atencion=atList)
            enfA = EnfermedadActual.objects.filter(atencion=atList)
            indic = Asignar.objects.filter(emergencia=idE)
            if len(enfA) > 0 and len(diags) > 0:
                historia_medica = True
            if len(diags) > 0:
                constancia = True
            if len(indic) > 0:
                indicaciones = True
    else:
        t = None

    info = {
        'p': p,
        'ea': ea,
        't': t,
        'hm_habilitado': historia_medica,
        'const_habilitado': constancia, 'ind_habilitado': indicaciones
        }
    return render_to_response(
        'app_perfil/perfil.html', info,
        context_instance=RequestContext(request)
        )
