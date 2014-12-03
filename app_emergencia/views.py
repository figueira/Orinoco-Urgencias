# -*- encoding: utf-8 -*-
# coding: latin1

# Manejo de Sesion
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy


# Formularios
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib import messages
from django.views import generic

# General HTML
from django.shortcuts import render_to_response, redirect,\
    get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect

# Manejo de Informacion de esta aplicacion
from django.utils.timezone import utc
from datetime import datetime, date, timedelta
from models import *
from forms import *
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
# from reportlab.pdfgen import canvas
# from reportlab.lib.units import inch
# from reportlab.platypus import Table, TableStyle
# from reportlab.platypus.flowables import *
# from reportlab.lib.colors import pink, black, red, lightblue, white

import cgi
import json
from django.template.loader import render_to_string

from app_enfermedad.models import *
from app_paciente.models import *
# from itertools import izip
from app_emergencia.pdf import *
from app_historiaMedica.views import paciente_perfil_emergencia
######################################################

from django.views import generic

# Cantidad de segundos en 1,2,..,6 horas
# hora_en_segundos[0] -> Segundos en 0 horas
# hora_en_segundos[1] -> Segundos en 1 hora
# .
# .
# .
# hora_en_segundos[6] -> Segundos en 6 horas
hora_en_segundos = [0, 3600, 7200, 10800, 14400, 18000, 21600]


def emergencia_buscar(request):
    mensaje = ""
    titulo = "Búsqueda de Pacientes"
    boton = "Buscar"
    info = {}
    form = IniciarSesionForm()
    if request.method == 'POST':
        busqueda = BuscarEmergenciaForm(request.POST)
        resultados = []
        if busqueda.is_valid():
            pcd = busqueda.cleaned_data
            p_cedula = pcd['cedula']
            p_nombres = pcd['nombres']
            p_apellidos = pcd['apellidos']

            if len(p_cedula) > 0:
                print "Se busco por cedula"
                print p_cedula
                pacientes = Paciente.objects.filter(
                    cedula__icontains=p_cedula).order_by('apellidos')
                if len(pacientes) > 0:
                    for p in pacientes:
                        resultados.append(p)
            else:
                print "Se busco por NO cedula"
                print "nombres:"+p_nombres+"y apellidos "+p_apellidos
                if len(p_nombres) > 0 and len(p_apellidos) > 0:
                    print "Se busco por Nombre y Apellido"
                    pacientes = Paciente.objects.filter(
                        nombres__icontains=p_nombres,
                        apellidos__icontains=p_apellidos).order_by('apellidos')
                    if len(pacientes) > 0:
                        for p in pacientes:
                            resultados.append(p)
                elif len(p_apellidos) == 0:
                    print "Se busco por Nombre"
                    pacientes = Paciente.objects.filter(
                        nombres__icontains=p_nombres).order_by('apellidos')
                    if pacientes:
                        for p in pacientes:
                            resultados.append(p)
                elif len(p_nombres) == 0:
                    print "Se busco por Apellido"
                    pacientes = Paciente.objects.filter(
                        apellidos__icontains=p_apellidos).order_by('apellidos')
                    if pacientes:
                        for p in pacientes:
                            resultados.append(p)
            lista = []
            for p in resultados:
                emergencias = Emergencia.objects.filter(
                    paciente=p).order_by('-hora_ingreso')
                for e in emergencias:
                    if e not in lista:
                        lista.append(e)

        # print "LA NUEVA ES: \n"
        # print list(set(lista))

            info = {
                'form': form,
                'lista': lista,
                'titulo': titulo,
                'resultados': resultados
            }
            return render_to_response(
                'listaB.html',
                info,
                context_instance=RequestContext(request))
    else:
        busqueda = BuscarEmergenciaForm()

    info = {
        'form': form,
        'busqueda': busqueda,
        'titulo': titulo,
        'boton': boton
    }
    return render_to_response(
        'busqueda.html',
        info,
        context_instance=RequestContext(request))

#   Busca en la base de datos las emergencias
# y los
#   cubiculos que seran utilizados en la vista lista.hmtl
#


def emergencia_listar_todas(request, mensaje=''):
    emergencias = Emergencia.objects.filter(hora_egreso=None) \
        .order_by('paciente__apellidos')
    cubiculos = Cubiculo.objects.all()

    form = IniciarSesionForm()
    titulo = "Área de emergencias"
    cabecera = "Listado General"
    buscar_enfermedad = False
    info = {
        'emergencias': emergencias,
        'cubiculos': cubiculos,
        'form': form,
        'mensaje': mensaje,
        'titulo': titulo,
        'cabecera': cabecera,
        'buscadorDeEnfermedad': buscar_enfermedad
    }
    return render(
        request,
        'lista.html',
        info,
        context_instance=RequestContext(request)
        )


def emergencia_listar_triage(request):
    # En el area de triage se listan todos los pacientes que no tienen cubiculo
    # asignado y no han sido egresados
    emergencias = Emergencia.objects \
        .filter(
            asignarcub__isnull=True,
            hora_egreso=None).distinct().order_by('hora_ingreso')
    form = IniciarSesionForm()
    titulo = "Área de triage"
    cabecera = "Área de Triage"
    buscar_enfermedad = False
    cubiculos = Cubiculo.objects.all()
    info = {
        'emergencias': emergencias,
        'form': form,
        'titulo': titulo,
        'cabecera': cabecera,
        'cubiculos': cubiculos,
        'buscadorDeEnfermedad': buscar_enfermedad
    }
    return render_to_response(
        'lista.html',
        info,
        context_instance=RequestContext(request))


def emergencia_listar_sinclasificar(request):
    emergencias = Emergencia.objects.filter(
        hora_egreso=None,
        triage__isnull=True).order_by('hora_ingreso')
    form = IniciarSesionForm()
    titulo = "Sin clasificar"
    cabecera = "Pacientes por Clasificar"
    buscar_enfermedad = False
    cubiculos = Cubiculo.objects.all()
    info = {
        'emergencias': emergencias,
        'form': form,
        'titulo': titulo,
        'cabecera': cabecera,
        'cubiculos': cubiculos,
        'buscadorDeEnfermedad': buscar_enfermedad
    }
    return render_to_response(
        'lista.html',
        info,
        context_instance=RequestContext(request))


def emergencia_listar_clasificados(request):
    emergencias = Emergencia.objects \
        .filter(
            hora_egreso=None,
            triage__isnull=False,
            asignarcub__isnull=True).distinct().order_by(
            'hora_ingreso'
            )
    form = IniciarSesionForm()
    titulo = "Clasificados"
    cabecera = "Pacientes Clasificados (No Atendidos)"
    buscar_enfermedad = False
    cubiculos = Cubiculo.objects.all()
    info = {
        'emergencias': emergencias,
        'form': form,
        'titulo': titulo,
        'cabecera': cabecera,
        'cubiculos': cubiculos,
        'buscadorDeEnfermedad': buscar_enfermedad
    }
    return render_to_response(
        'lista.html',
        info,
        context_instance=RequestContext(request))


def emergencia_listar_atencion(request):
    emergencias = Emergencia.objects.filter(
        hora_egreso=None,
        triage__isnull=False,
        asignarcub__isnull=False
    ).distinct().order_by('hora_ingreso')
    form = IniciarSesionForm()
    titulo = "Clasificados"
    cabecera = "Área de Atención"
    buscar_enfermedad = False
    cubiculos = Cubiculo.objects.all()
    info = {
        'emergencias': emergencias,
        'form': form,
        'titulo': titulo,
        'cabecera': cabecera,
        'cubiculos': cubiculos,
        'buscadorDeEnfermedad': buscar_enfermedad
    }
    return render_to_response(
        'lista.html',
        info,
        context_instance=RequestContext(request))


def emergencia_buscar_historia_medica(request):
    titulo = "Búsqueda de Pacientes"
    boton = "Buscar"
    info = {}
    form = IniciarSesionForm()
    if request.method == 'POST':
        busqueda = BuscarEmergenciaForm(request.POST)
        resultados = []
        if busqueda.is_valid():
            pcd = busqueda.cleaned_data
            p_cedula = pcd['cedula']
            p_nombres = pcd['nombres']
            p_apellidos = pcd['apellidos']

            if len(p_cedula) > 0:
                pacientes = Paciente.objects.filter(
                    cedula__icontains=p_cedula
                ).order_by('apellidos')
                if len(pacientes) > 0:
                    for p in pacientes:
                        resultados.append(p)
            else:
                if len(p_nombres) > 0 and len(p_apellidos) > 0:
                    pacientes = Paciente.objects.filter(
                        nombres__icontains=p_nombres,
                        apellidos__icontains=p_apellidos
                    ).order_by('apellidos')
                    if len(pacientes) > 0:
                        for p in pacientes:
                            resultados.append(p)
                elif len(p_apellidos) == 0:
                    pacientes = Paciente.objects.filter(
                        nombres__icontains=p_nombres
                    ).order_by('apellidos')
                    if pacientes:
                        for p in pacientes:
                            resultados.append(p)
                elif len(p_nombres) == 0:
                    pacientes = Paciente.objects.filter(
                        apellidos__icontains=p_apellidos
                    ).order_by('apellidos')
                    if pacientes:
                        for p in pacientes:
                            resultados.append(p)
            lista = []
            for p in resultados:
                emergencias = Emergencia.objects.filter(
                    paciente=p,
                    triage__isnull=False).distinct().order_by('-hora_ingreso')
                for e in emergencias:
                    if e not in lista:
                        lista.append(e)

        info = {
            'form': form,
            'lista': lista,
            'titulo': titulo
        }
        return render_to_response(
            'listaC.html',
            info,
            context_instance=RequestContext(request))
    else:
        busqueda = BuscarEmergenciaForm()

    info = {
        'form': form,
        'busqueda': busqueda,
        'titulo': titulo,
        'boton': boton
    }
    return render_to_response(
        'busqueda.html',
        info,
        context_instance=RequestContext(request))


def emergencia_listar_observacion(request, mensaje=''):
    emergencias = Emergencia.objects.filter(
        hora_egreso=None, triage__nivel__range=[1, 3]).order_by(
        'hora_ingreso'
    )
    form = IniciarSesionForm()
    titulo = "Observación"
    cabecera = "Área de Observación"
    buscarEnfermedad = True
    cubiculos = Cubiculo.objects.all()
    info = {
        'emergencias': emergencias,
        'form': form,
        'titulo': titulo,
        'cabecera': cabecera,
        'cubiculos': cubiculos,
        'mensaje': mensaje,
        'buscadorDeEnfermedad': buscarEnfermedad
    }
    return render_to_response(
        'lista.html',
        info,
        context_instance=RequestContext(request))


def emergencia_listar_ambulatoria(request, mensaje=''):
    emergencias = Emergencia.objects.filter(
        hora_egreso=None,
        triage__nivel__range=[4, 5]).order_by('hora_ingreso')
    form = IniciarSesionForm()
    titulo = "Ambulatorio"
    cabecera = "Área de Atención Ambulatoria"
    buscar_enfermedad = True
    cubiculos = Cubiculo.objects.all()
    info = {
        'emergencias': emergencias,
        'form': form,
        'titulo': titulo,
        'cabecera': cabecera,
        'cubiculos': cubiculos,
        'mensaje': mensaje,
        'buscadorDeEnfermedad': buscar_enfermedad
    }
    return render_to_response(
        'lista.html',
        info,
        context_instance=RequestContext(request))


def emergencia_listar_cubiculos(request, mensaje=''):
    emergencias = Emergencia.objects.filter(
        hora_egreso=None)
    asignaciones = Cubiculo.objects.all().exclude(emergencia=None)
    titulo = "Cubiculos"
    cabecera = "Asignaciones de Cubiculos"
    cubiculos = Cubiculo.objects.all()
    info = {
        'emergencias': emergencias,
        'asignaciones': asignaciones,
        'titulo': titulo,
        'cabecera': cabecera,
        'cubiculos': cubiculos
    }
    return render_to_response(
        'listaCubiculos.html',
        info,
        context_instance=RequestContext(request))


@login_required(login_url='/')
def emergencia_agregar(request):
    mensaje = ""
    msj_tipo = ""
    msj_info = ""
    if request.method == 'POST':
        form = AgregarEmergenciaForm(request.POST)
        if form.is_valid():
            pcd = form.cleaned_data
            p_cedula = pcd['cedula']
            p_documento = pcd['documento']
            p_nombres = pcd['nombres']
            p_apellidos = pcd['apellidos']
            p_sexo = pcd['sexo']
            p_fecha_nacimiento = pcd['fecha_nacimiento']
            #
            # NOTA:
            # Codigo viejo, cambiado por uno mas efeciente.
            # Todavia se puede optimizar con un modelFORM
            #
            # print p_fecha_nacimiento
            # prueba = Paciente.objects.filter(cedula=p_cedula)
            # if len(prueba) == 0:
            #     p = Paciente(
            #         cedula=p_documento + str(p_cedula),
            #         nombres=p_nombres,
            #         apellidos=p_apellidos,
            #         sexo=p_sexo,
            #         fecha_nacimiento=p_fecha_nacimiento,
            #         tlf_cel="",
            #         email="",
            #         direccion="",
            #         tlf_casa="",
            #         contacto_rel=11,
            #         contacto_nom="",
            #         contacto_tlf="")
            #     p.save()
            try:

                p, creado = Paciente.objects.get_or_create(
                    cedula=p_documento + str(p_cedula),
                    nombres=p_nombres,
                    apellidos=p_apellidos,
                    sexo=p_sexo,
                    fecha_nacimiento=p_fecha_nacimiento,
                    tlf_cel="",
                    email="",
                    direccion="",
                    tlf_casa="",
                    contacto_rel=11,
                    contacto_nom="",
                    contacto_tlf=""
                )
            except:
                creado = False
                paciente = Paciente.objects.get(
                    cedula=p_documento + str(p_cedula)
                )
                messages.add_message(
                    request,
                    messages.ERROR,
                    'Ya existe un paciente con esta cedula. &nbsp;&nbsp;'
                    +
                    '<a target="_blank" href="/paciente/'
                    + str(paciente.id) +
                    '" class="btn btn-xs '
                    +
                    'btn-warning" > Ir al paciente </a>',
                    extra_tags='danger'
                )
                info = {
                    'form': form
                }
                return render_to_response(
                    'agregarPaciente.html',
                    info,
                    context_instance=RequestContext(request))
            # else:
            #     p = prueba[0]
            e_activa = len(Emergencia.objects.filter(
                paciente=p).filter(hora_egreso__isnull=True))
            if e_activa == 0:
                try:
                    e_ingreso = Usuario.objects.get(
                        username=request.user)
                except:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        'No tiene permisos para agregar un nuevo paciente',
                        extra_tags='danger'
                    )
                    return render_to_response(
                        'agregarPaciente.html',
                        {'form': form},
                        context_instance=RequestContext(request))
                e_responsable = e_ingreso
                e_horaIngreso = pcd['ingreso']
                e_horaIngresoReal = datetime.now()
                e = Emergencia(
                    paciente=p,
                    responsable=e_responsable,
                    ingreso=e_ingreso,
                    hora_ingreso=e_horaIngreso,
                    hora_ingresoReal=e_horaIngresoReal,
                    hora_egreso=None
                )
                e.save()
                espe = get_object_or_404(Espera, nombre='Ubicacion')
                espera1 = EsperaEmergencia(
                    espera=espe,
                    emergencia=e,
                    estado='0'
                )
                espera1.save()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Paciente agregado con éxito'
                )
                return HttpResponseRedirect('/emergencia/listar/todas')
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    'Este usuario ya tiene una \
                    emergencia actual sin atender',
                    extra_tags='danger'
                )
                msj_tipo = "error"
                msj_info = "Ya este usuario esta en una emergencia.\
                    No puede ingresar a un usuario 2 veces a la emergencia"

        info = {
            'form': form,
            'msj_tipo': msj_tipo,
            'msj_info': msj_info
            }
        return render_to_response(
            'agregarPaciente.html',
            info,
            context_instance=RequestContext(request))

    form = AgregarEmergenciaForm()
    info = {
        'form': form
    }
    return render_to_response(
        'agregarPaciente.html',
        info,
        context_instance=RequestContext(request))


@login_required(login_url='/')
def emergencia_agrega_emer(request, id_emergencia):
    emergencia = get_object_or_404(Emergencia, id=id_emergencia)
    p = Paciente.objects.filter(id=emergencia.paciente.id)
    e_activa = len(Emergencia.objects.filter(paciente=p[0]).filter(
        hora_egreso__isnull=True))
    if e_activa == 0:
        e_ingreso = Usuario.objects.get(username=request.user)
        e_responsable = e_ingreso
        e_horaIngreso = datetime.now()
        e_horaIngresoReal = datetime.now()
        e = Emergencia(
            paciente=p[0],
            responsable=e_responsable,
            ingreso=e_ingreso,
            hora_ingreso=e_horaIngreso,
            hora_ingresoReal=e_horaIngresoReal,
            hora_egreso=None
        )
        e.save()
        espe = get_object_or_404(
            Espera,
            nombre='Ubicacion'
        )
        espera1 = EsperaEmergencia(
            espera=espe,
            emergencia=e,
            estado='0')
        espera1.save()
        # print "Creando nueva emergencia objeto creado: ",e
        return HttpResponseRedirect('/emergencia/listar/todas')
    else:
        messages.add_message(
            request,
            messages.ERROR,
            'Ya este usuario esta en una emergencia.'
            +
            'No puede ingresar a un usuario 2 veces a la emergencia',
            extra_tags='danger'
        )
        # msj_tipo = "error"
        # msj_info = "Ya este usuario esta en una emergencia.Nopuede ingresar \
        #     a un usuario 2 veces a la emergencia"
        # mensaje = "Ya este usuario esta en una emergencia.\
        # No puede ingresar a un usuario 2 veces a la emergencia"
        # print " ya este paciente tiene una emergencia activa"
        # info = {'mensaje':mensaje}
        # return render_to_response(
        #       'listaB.html',info,context_instance=RequestContext(request))
        return HttpResponseRedirect('/emergencia/listar/todas')


@login_required(login_url='/')
def emergencia_cubiculo_liberar(request, idA):
    cubiculo = Cubiculo.objects.filter(emergencia=idA).first()
    # cubiculo = get_object_or_404(Cubiculo, id=idA)
    cubiculo.emergencia = None
    cubiculo.save()
    # asigCA = AsignarCub.objects.filter(id=idA)
    # if asigCA:
    #     asigCA.delete()
    return HttpResponseRedirect("/emergencia/listar/cubiculos")

@login_required(login_url='/')
def emergencia_darAlta(request, idE):
    emergencia = get_object_or_404(Emergencia, id=idE)
    try:
        medico = Usuario.objects.get(username=request.user)
    except:
        return HttpResponseRedirect('/paciente/'+str(emergencia.paciente.id))
    if (medico.tipo == "1"):
        if request.method == 'POST':
            form = darAlta(request.POST)
            if form.is_valid():
                # Iniciar una transaccion para asegurar que las dos
                # operaciones se
                # realicen
                with transaction.atomic():
                    pcd = form.cleaned_data
                    f_destino = pcd['destino']
                    f_area = pcd['area']
                    f_darAlta = pcd['darAlta']
                    f_traslado = pcd['traslado']
                    emergencia.egreso = medico
                    emergencia.hora_egreso = f_darAlta
                    emergencia.hora_egresoReal = datetime.now()
                    emergencia.destino = f_destino

                    emergencia.save()

                    # Liberar el cubiculo que estaba asignado
                    cubiculo = Cubiculo.objects.filter(
                        emergencia=emergencia).first()
                    if cubiculo is not None:
                        cubiculo.emergencia = None
                        cubiculo.save()
                    else:
                        print "Dando de alta sin cubiculo asignado"

                    # Si habia alguna espera activa, marcarla como atendida
                    esperas = EsperaEmergencia.objects.filter(
                        emergencia=emergencia,
                        hora_fin=None
                    )
                    for espera in esperas:
                        espera.hora_fin = f_darAlta
                        espera.save()

            else:
                info = {
                    'form': form,
                    'emergencia': emergencia
                }
                return render_to_response(
                    'darAlta.html',
                    info,
                    context_instance=RequestContext(request))
        else:
            form = darAlta()
            info = {
                'form': form,
                'emergencia': emergencia
            }
            return render_to_response(
                'darAlta.html',
                info,
                context_instance=RequestContext(request))
    return HttpResponseRedirect("/emergencia/listar/todas")


@login_required(login_url='/')
def emergencia_aplicarTriage(request, idE, vTriage):
    emergencia = get_object_or_404(Emergencia, id=idE)
    triage = get_object_or_404(Triage, emergencia=emergencia)
    recursos = 2
    atencion = False
    esperar = False
    if (vTriage == ''):
        # El paciente debe ser evaluado para asignarle un triage
        if(
            (triage.signos_tmp < 37 or 38.4 < triage.signos_tmp) or
            (triage.signos_fc < 60 or 100 < triage.signos_fc) or
            (triage.signos_fr < 14 or 20 < triage.signos_fr) or
            (triage.signos_pa < 60 or 89 < triage.signos_pa) or
            (triage.signos_pb < 100 or 139 < triage.signos_pb) or
            (triage.signos_saod < 95 or 100 < triage.signos_saod)
        ):
            vTriage = "2"
        else:
            vTriage = "3"

    if (vTriage == "1"):
        atencion = True
    elif (vTriage == "2"):
        atencion = False
        esperar = False
    else:
        if (vTriage == "4"):
            recursos = 1
        elif (vTriage == "5"):
            recursos = 0
        atencion = False
        esperar = True

    triage.atencion = atencion
    triage.esperar = esperar
    triage.recursos = recursos
    triage.nivel = vTriage
    triage.save()
    return redirect('/emergencia/listar/todas')


@login_required(login_url='/')
def actualizarSignos(request, idE):
    emergencia = get_object_or_404(Emergencia, id=idE)
    triage = get_object_or_404(Triage, emergencia=emergencia)

    if request.method == 'POST':
        form = ActualizarSignosForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            avpus = data['avpu']
            fc = data['frecuencia_cardiaca']
            fr = data['frecuencia_respiratoria']
            ps = data['presion_sistolica']
            pd = data['presion_diastolica']
            so = data['saturacion_oxigeno']
            temp = data['temperatura']
            dolor = data['intensidad_dolor']
            triage.signos_avpu = avpus
            triage.signos_fc = fc
            triage.signos_fr = fr
            triage.signos_pa = ps
            triage.signos_pb = pd
            triage.signos_saod = so
            triage.signos_tmp = temp
            triage.signos_dolor = dolor

            triage.save()
        else:
            info = {
                'form': form,
                'emergencia': emergencia,
                'triage': triage
            }
            return render_to_response(
                'actualizarSignos.html',
                info,
                context_instance=RequestContext(request))
    else:
        form = ActualizarSignosForm()
        info = {
            'form': form,
            'emergencia': emergencia,
            'triage': triage
        }
        return render_to_response(
            'actualizarSignos.html',
            info,
            context_instance=RequestContext(request))

    return redirect('/emergencia/atencion/'+idE+'/historia')


@login_required(login_url='/')
def emergencia_calcular_triage(request, idE, triage_asignado):
    if triage_asignado:
        triage_inicial = None
    else:
        triage_inicial = None
    mensaje = ""
    form = FormularioEvaluacionPaciente()
    info = {
        'form': FormularioEvaluacionPaciente(initial=triage_inicial),
        'idE': idE,
        'triage_asignado': triage_asignado
    }
    return render_to_response(
        'calcularTriage.html',
        info,
        context_instance=RequestContext(request))


def estadisticas_prueba():
    #    triages = Triage.objects.filter(fecha__year=ano).
    #        filter(fecha__month=mes).values('nivel').
    #           annotate(Count('nivel')).order_by('nivel')
    #    triages = [[i['nivel'],i['nivel__count']] for i in triages]
    #    triagesBien = [[1,0],[2,0],[3,0],[4,0],[5,0]]
    #    for i in triages:
    #      triagesBien[i['nivel']] = i['count']
    triages = Triage.objects.all().values(
        'nivel'
    ).annotate(Count('nivel')).order_by('nivel')
    triages = [
        [i['nivel'], i['nivel__count']] for i in triages]
    triagesBien = [0, 0, 0, 0, 0]
    for i in triages:
        triagesBien[i[0]-1] = i[1]
    triages = []
    for i in range(5):
        triages.append([(i+1), triagesBien[i]])
    return triages


def obtener_imagenes():
    objetos_causas_de_espera = Espera.objects.all()
    imagenes = []
    for espera in objetos_causas_de_espera:
        imagenes.append(espera.url_imagen)
    return imagenes


def ordenar_por_causas(diccionario_de_causas):
    resultado = sorted(
        diccionario_de_causas.items(),
        key=lambda t: t[0]
    )
    return resultado


def ordenar_por_color(diccionario_de_causas):
    resultado = [
        ('Verde', diccionario_de_causas['Verde']),
        ('Amarillo', diccionario_de_causas['Amarillo']),
        ('Rojo', diccionario_de_causas['Rojo']),
        ('Negro', diccionario_de_causas['Negro'])
    ]
    return resultado


def ordenar_por_color_transicion(diccionario_de_causas):
    resultado = [
        ('Amarillo', diccionario_de_causas['Amarillo']),
        ('Rojo', diccionario_de_causas['Rojo']),
        ('Negro', diccionario_de_causas['Negro'])
    ]
    return resultado


def obtener_causas_de_espera(emergencias):
    # Diccionario que mapea el nombre de la causa de espera
    # a un arreglo indicando la cantidad de ocurrencias por
    # intervalo de duracion
    # Ej: '[[Ubicacion, [0,2,3,1]], [Laboratorio, [2,0,4,4]]]'
    causas_de_espera = {}
    causas_transicion = {}

    objetos_causas_de_espera = Espera.objects.all()
    for causa in objetos_causas_de_espera:
        causas_de_espera[causa.nombre] = ([0, 0, 0, 0], causa.url_imagen())
        causas_transicion[causa.nombre] = ([0, 0, 0], causa.url_imagen())

    for emergencia in emergencias:
        espera_emergencias = EsperaEmergencia.objects.filter(
            emergencia=emergencia
        )
        hora_inicio_emergencia = emergencia.hora_ingreso
        for espera_emergencia in espera_emergencias:
            causa = espera_emergencia.espera.nombre
            if espera_emergencia.hora_fin is None:
                continue
            tiempo_espera = (
                espera_emergencia.hora_fin -
                espera_emergencia.hora_comienzo
            ).seconds
            if tiempo_espera < hora_en_segundos[2]:
                grupo = 0
            elif (
                hora_en_segundos[2] <= tiempo_espera
                and tiempo_espera < hora_en_segundos[4]
            ):
                grupo = 1
            elif (
                hora_en_segundos[4] <= tiempo_espera
                and tiempo_espera < hora_en_segundos[6]
            ):
                grupo = 2
            else:
                grupo = 3

            dif_inicio = (
                espera_emergencia.hora_comienzo - hora_inicio_emergencia
            ).seconds
            dif_fin = (
                espera_emergencia.hora_fin - hora_inicio_emergencia
            ).seconds

            if dif_inicio < hora_en_segundos[2]:
                grupo_trans_inicio = -1
            elif(
                hora_en_segundos[2] <= dif_inicio
                and dif_inicio < hora_en_segundos[4]
            ):
                grupo_trans_inicio = 0
            elif(
                hora_en_segundos[4] <= dif_inicio
                and dif_inicio < hora_en_segundos[6]
            ):
                grupo_trans_inicio = 1
            else:
                grupo_trans_inicio = 2

            if dif_fin < hora_en_segundos[2]:
                grupo_trans_fin = -1
            elif (
                hora_en_segundos[2] <= dif_fin
                and dif_fin < hora_en_segundos[4]
            ):
                grupo_trans_fin = 0
            elif(
                hora_en_segundos[4] <= dif_fin
                and dif_fin < hora_en_segundos[6]
            ):
                grupo_trans_fin = 1
            else:
                grupo_trans_fin = 2

            (valores, img) = causas_de_espera[causa]
            valores[grupo] += 1

            if (grupo_trans_fin == grupo_trans_inicio):
                continue

            grupo_trans = max(grupo_trans_fin, grupo_trans_inicio)
            (valores_trans, img_trans) = causas_transicion[causa]
            valores_trans[grupo_trans] += 1

    return (causas_de_espera, causas_transicion)


def invertir_orden_de_diccionario(diccionario, colores):
    pos_negro = len(colores)-1

    intermedio = []
    for causa in diccionario.keys():
        intermedio.append((causa, diccionario[causa]))
    intermedio = sorted(intermedio, key=lambda t: -t[1][0][pos_negro])

    causas_invertidas = []
    for color in colores:
        causas_invertidas.append((color, []))

    aux = [x[0] for x in causas_invertidas]
    for causa in intermedio:
        (valores, img) = causa[1]
        for i in range(0, len(colores)):
            causas_invertidas[aux.index(colores[i])][1].append(
                (causa[0], valores[i]))
    return causas_invertidas


def estadisticas_per(request, dia, mes, anho, dia2, mes2, anho2):
    # Datos generales
    fecha_inicio = date(int(anho), int(mes), int(dia))
    fecha_fin = date(int(anho2), int(mes2), int(dia2))
    siguiente_semana = fecha_fin + timedelta(days=7)
    ingresos_emergencia = Emergencia.objects.filter(
        hora_ingreso__range=[fecha_inicio, fecha_fin])
    egresos_emergencia = Emergencia.objects.filter(
        hora_egreso__range=[fecha_inicio, fecha_fin])

    # Cantidad de emergencias por duracion
    # horas[0] -> 0 a 2 horas
    # horas[1] -> 2 a 4 horas
    # horas[2] -> 4 a 6 horas
    # horas[3] -> 6 o + horas
    horas = [0, 0, 0, 0]

    # Emergencias por duracion
    # emergencias_por_horas[0] -> 0 a 2 horas
    # emergencias_por_horas[1] -> 2 a 4 horas
    # emergencias_por_horas[2] -> 4 a 6 horas
    # emergencias_por_horas[3] -> 6 o + horas
    emergencias_por_horas = [[], [], [], []]

    for egreso in egresos_emergencia:
        t = egreso.tiempo_emergencia()
        if t < hora_en_segundos[2]:
            grupo = 0
        elif hora_en_segundos[2] <= t and t < hora_en_segundos[4]:
            grupo = 1
        elif hora_en_segundos[4] <= t and t < hora_en_segundos[6]:
            grupo = 2
        else:
            grupo = 3

        horas[grupo] += 1
        emergencias_por_horas[grupo].append(egreso)
    total_egresos = sum(horas)

    # Causas de espera por grupo
    (causas_pacientes_en_negro, causas_transicion_negro) = \
        obtener_causas_de_espera(emergencias_por_horas[3])
    (causas_pacientes_en_rojo, causas_transicion_rojo) = \
        obtener_causas_de_espera(emergencias_por_horas[2])
    (causas_pacientes_en_amarillo, causas_transicion_amarillo) = \
        obtener_causas_de_espera(emergencias_por_horas[1])
    (causas_pacientes_en_verde, causas_transicion_verde) = \
        obtener_causas_de_espera(emergencias_por_horas[0])
    total_causas = len(causas_pacientes_en_amarillo)
    causas_de_espera = Espera.objects.all()
    causas_pacientes_total = {}
    for causa in causas_de_espera:
        (causa_ver, img_ver) = causas_pacientes_en_verde[causa.nombre]
        (causa_ama, img_ama) = causas_pacientes_en_amarillo[causa.nombre]
        (causa_roj, img_roj) = causas_pacientes_en_rojo[causa.nombre]
        (causa_neg, img_neg) = causas_pacientes_en_negro[causa.nombre]
        causas_pacientes_total[causa.nombre] = ([
            sum([causa_ver[0], causa_ama[0], causa_roj[0], causa_neg[0]]),
            sum([causa_ver[1], causa_ama[1], causa_roj[1], causa_neg[1]]),
            sum([causa_ver[2], causa_ama[2], causa_roj[2], causa_neg[2]]),
            sum([causa_ver[3], causa_ama[3], causa_roj[3], causa_neg[3]])
        ], causa.url_imagen())
    causas = [
        ('General', ordenar_por_causas(
            causas_pacientes_total)),
        ('Verde', ordenar_por_causas(
            causas_pacientes_en_verde)),
        ('Amarillo', ordenar_por_causas(
            causas_pacientes_en_amarillo)),
        ('Rojo', ordenar_por_causas(
            causas_pacientes_en_rojo)),
        ('Negro', ordenar_por_causas(
            causas_pacientes_en_negro))
    ]
    causas_transicion = [
        ('Amarillo', ordenar_por_causas(
            causas_transicion_amarillo)),
        ('Rojo', ordenar_por_causas(
            causas_transicion_rojo)),
        ('Negro', ordenar_por_causas(
            causas_transicion_negro))
    ]

    imaganes = obtener_imagenes()

    lista_auxiliar = [
        causas_pacientes_en_verde,
        causas_pacientes_en_amarillo,
        causas_pacientes_en_rojo,
        causas_pacientes_en_negro
    ]
    lista_auxiliar_transicion = [
        causas_transicion_amarillo,
        causas_transicion_rojo,
        causas_transicion_negro
    ]

    colores = [
        'Verde', 'Amarillo', 'Rojo', 'Negro'
    ]
    colores_transicion = ['Amarillo', 'Rojo', 'Negro']
    causas_invertidas = []
    for x, y in zip(lista_auxiliar, colores):
        causas_invertidas.append(
            (y, invertir_orden_de_diccionario(x, colores)))
    causas_transicion_invertidas = []
    for x, y in zip(lista_auxiliar_transicion, colores_transicion):
        causas_transicion_invertidas.append(
            (y, invertir_orden_de_diccionario(
                x,
                colores_transicion)))

    causas_invertidas = [
        ('General', invertir_orden_de_diccionario(
            causas_pacientes_total, colores))
    ] + causas_invertidas
    # Resultados de los Triages
    triages = Triage.objects.filter(fecha__range=[fecha_inicio, fecha_fin])\
        .values('nivel').annotate(Count('nivel')).order_by('nivel')
    triages = [[i['nivel'], i['nivel__count']] for i in triages]
    triagesBien = [0, 0, 0, 0, 0]
    for i in triages:
        triagesBien[i[0]-1] = i[1]
    triages = []
    for i in range(5):
        triages.append([(i+1), triagesBien[i]])
    egresos = [
        ['Total', total_egresos], ['Verde (0 a 2 horas)', horas[0]],
        ['Amarillo (2 a 4 horas)', horas[1]], ['Rojo (4 a 6 horas)', horas[2]],
        ['Negro (6 o + horas)', horas[3]]
    ]

    prueba = invertir_orden_de_diccionario(lista_auxiliar[3], colores)

    info = {
        'triages': triages,
        'fecha': date.today(),
        'inicio': fecha_inicio,
        'fin': fecha_fin,
        'sig': siguiente_semana,
        'total_ingresos': len(ingresos_emergencia),
        'total_egresos': total_egresos,
        'egresos': egresos,
        'emergencias': emergencias_por_horas,
        'causas': causas,
        'imagenes': imaganes,
        'causas_transicion': causas_transicion,
        'causas_invertidas': causas_invertidas,
        'causas_transicion_invertidas': causas_transicion_invertidas,
        'colores': colores,
        'colores_transicion': colores_transicion,
        'lista_auxiliar': lista_auxiliar,
        'prueba': prueba
    }
    return render_to_response(
        'estadisticas.html',
        info,
        context_instance=RequestContext(request))


def estadisticas_sem(request, dia, mes, anho):
    fecha_fin = datetime(int(anho), int(mes), int(dia))
    fecha_inicio = fecha_fin - timedelta(weeks=1)
    return HttpResponseRedirect(
        '/estadisticas/' + str(fecha_inicio.day) + '-' +
        str(fecha_inicio.month) + '-' + str(fecha_inicio.year) +
        '/' + dia + '-' + mes + '-' + anho)


def estadisticas(request):
    hoy = datetime.today()
    return HttpResponseRedirect(
        '/estadisticas/'
        +
        str(hoy.day)
        +
        '-'
        +
        str(hoy.month)
        +
        '-'
        +
        str(hoy.year)
    )


#########################################################
#                                                       #
#          Views para Casos de Uso de Esperas           #
#                                                       #
#########################################################
def emergencia_espera_mantener(request, id_emergencia):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    emer.fecha_Esp_act = datetime.now()
    emer.save()
    return HttpResponse()

# Método que realiza la asociación en la base de datos de una espera a una
# emergencia. Devuelve una respuesta en JSON con el identificador de la entidad
# creada


def emergencia_agregar_espera(request, id_emergencia, id_espera):
    emergencia = get_object_or_404(Emergencia, id=id_emergencia)
    emergencia.fecha_Esp_act = datetime.now()
    emergencia.save()
    espera = get_object_or_404(Espera, id=id_espera)
    espera_emergencia = EsperaEmergencia(
        emergencia=emergencia,
        espera=espera,
        estado='0'
    )
    espera_emergencia.save()
    return HttpResponse(
        json.dumps(espera_emergencia.id),
        content_type='application/json')


def emergencia_eliminar_espera_emergencia(request, id_espera_emergencia):
    espera_emergencia = get_object_or_404(
        EsperaEmergencia,
        id=id_espera_emergencia)
    emergencia = espera_emergencia.emergencia
    emergencia.fecha_Esp_act = datetime.now()
    emergencia.save()
    espera_emergencia.delete()
    return HttpResponse()


def emergencia_espera_estado(request, id_emergencia, id_espera, espera):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    emer.fecha_Esp_act = datetime.now()
    emer.save()
    espe = get_object_or_404(Espera, id=id_espera)
    espera1 = EsperaEmergencia.objects.get(espera=espe, emergencia=emer)
    espera1.estado = str(espera)
    espera1.save()
    return HttpResponse()


def emergencia_espera_asignadasCheck(request, id_emergencia):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    esperasEmer = EsperaEmergencia.objects.filter(emergencia=emer)
    esperasEmer = [str(i.estado) for i in esperasEmer]
    esp = ""
    for i in esperasEmer:
        esp = esp+i+","
    return HttpResponse(esp)


def emergencia_espera_id(request, id_emergencia):
    esperas = EsperaEmergencia.objects.filter(emergencia__id=id_emergencia)
    esperas = [str(i.espera.id) for i in esperas]
    esp = ""
    for i in esperas:
        esp = esp+i+","
    return HttpResponse(esp)


def emergencia_espera_idN(request, id_emergencia):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    esperasEmer = EsperaEmergencia.objects.filter(emergencia=emer)
    esperasEmer = [str(i.espera.id) for i in esperasEmer]
    esperas = Espera.objects.filter()
    esperas = [str(i.id) for i in esperas]
    for EspEmer in esperasEmer:
        esperas.remove(EspEmer)
    esp = ""
    for i in esperas:
        esp = esp+i+","
    return HttpResponse(esp)


# Se agrega a la base de datos la fechay hora en que se marco check (finalizo)
# para una causa de espera para una emergencia
#


def emergencia_espera_finalizada(request, id_espera_emergencia):
    espera_emergencia = EsperaEmergencia.objects.get(id=id_espera_emergencia)
    espera_emergencia.hora_fin = datetime.now()
    espera_emergencia.save()
    return HttpResponse('')

#########################################################
#                                                       #
#             Guardar/ Actualizar Cubiculo              #
#                                                       #
#########################################################

# Funciones para agregar un cubiculo


def emergencia_guardar_cubi(request, id_emergencia, admin, accion):
    emergencia = get_object_or_404(Emergencia, id=id_emergencia)
    id_cubiculo = request.GET['id_cubiculo']
    if id_cubiculo == '':
        cubiculo = None
    else:
        cubiculo = get_object_or_404(Cubiculo, id=id_cubiculo)

    if (cubiculo is not None) and (cubiculo.esta_asignado()):
        messages.add_message(
            request,
            messages.ERROR,
            'El cubiculo ya  se encuentra asignado',
            extra_tags='danger'
        )
    else:
        if (
            (cubiculo is not None)
            and
            (not cubiculo.emergencia_asignada(id_emergencia))
        ):
            # Actualizar la causa de espera por ubicacion
            espera = get_object_or_404(Espera, nombre='Ubicacion')
            espera_emergencia = EsperaEmergencia.objects.filter(
                espera=espera, emergencia=emergencia).update(
                hora_fin=datetime.now())

            triage = Triage.objects.filter(
                emergencia=id_emergencia).order_by("-fechaReal").first()

            # triage = triage[0]
            atencion = Atencion.objects.create(
                emergencia=emergencia,
                medico=emergencia.responsable,
                fecha=datetime.now(),
                fechaReal=datetime.now(),
                area_atencion=triage.areaAtencion.id
            )

            # Aqui se garantiza que el 'cubiculo' no va a ser None,
            # puesto que se tuvo
            # que haber seleccionado un cubiculo para llegar aqui
            # asignacion_cubiculo = AsignarCub.objects.create(
            #     emergencia=emergencia,
            #     cubiculo=cubiculo
            # )
            cubiculo.emergencia = emergencia
            cubiculo.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                'Cubiculo asignado con exito'
            )
            # mensaje = "Logrado: Cubiculo " + cubiculo.nombre + " asignado"
        else:
            cubiculo_asignado = Cubiculo.objects.filter(
                emergencia_id=id_emergencia).last()
            if cubiculo is None:
                # Aqui se pidio no asignar ningun cubiculo
                # asignacion_cubiculo.delete()
                if cubiculo_asignado:
                    cubiculo_asignado.emergencia = None
                    cubiculo_asignado.save()
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        'Cubiculo liberado con exito'
                    )
            else:
                cubiculo_asignado.emergencia = None
                cubiculo_asignado.save()
                cubiculo.emergencia = emergencia
                cubiculo.save()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Cubiculo asignado con exito'
                )
        if cubiculo is None:
            return emergencia_listar_todas(request, mensaje=None)
    if admin == '1':
        return HttpResponseRedirect(reverse_lazy('listar_cubiculos'))
    else:
        return HttpResponseRedirect(reverse_lazy('listar_todas'))


# - Funciones para agregar un cubiculo


def emergencia_tiene_cubiculo(request, id_emergencia):
    emer = get_object_or_404(Emergencia, id=id_emergencia)
    cubi = request.POST[str(emer.id)+"cub"]
    asic = Cubiculo.objects.filter(asignarcub__cubiculo__nombre=cubi)
    if asic:
        mensaje = "si"
        return HttpResponse(mensaje)
    else:
        mensaje = "no"
        return HttpResponse(mensaje)


class formulario_busqueda_cedula(generic.ListView):

    def get_data(self, cedula=None):
        if not cedula:
            cedula = None
            return None
        data = []
        resultados = []
        pacientes = Paciente.objects.filter(
            cedula=cedula).order_by('apellidos')

        if len(pacientes) > 0:
            for paciente in pacientes:
                resultados.append(paciente)

        for resultado in resultados:
            emergencias = Emergencia.objects.filter(
                paciente=resultado).order_by('paciente__apellidos')
            for emergencia in emergencias:
                    if emergencia not in data:
                        data.append(emergencia)
        return data

    def get(self, request, *args, **kwargs):
        return render_to_response(
            'app_emergencia/busquedaCedula.html',
            {
                'get': True,
                'formulario': buscar_por_cedulaForm()
            },
            context_instance=RequestContext(request)
        )

    def post(self, request, *args, **kwargs):
        formulario = buscar_por_cedulaForm(request.POST)

        if formulario.is_valid():
            cedula = formulario.cleaned_data['cedula']
            documento = formulario.cleaned_data['documento']
            cedula = documento+str(cedula)
        return render_to_response(
            'app_emergencia/busquedaCedula.html',
            {
                'lista': self.get_data(cedula=cedula),
                'formulario': formulario,
            },
            context_instance=RequestContext(request)
        )


class formulario_busqueda_nombre(generic.ListView):

    def get_data(self, nombre=None, apellido=None):
        resultados = []
        pacientes = ''
        data = []
        if nombre and apellido:
            print 'Nombre y Apellido'
            pacientes = Paciente.objects.filter(
                nombres__icontains=nombre,
                apellidos__icontains=apellido).order_by('apellidos')

        elif nombre:
            print'Nombre'
            pacientes = Paciente.objects.filter(
                nombres__icontains=nombre).order_by('apellidos')
        elif apellido:
            print 'Apellido'
            pacientes = Paciente.objects.filter(
                apellidos__icontains=apellido).order_by('apellidos')

        # print pacientes
        if len(pacientes) > 0:
            for paciente in pacientes:
                resultados.append(paciente)
        # print resultados
        for paciente in resultados:
            emergencias = Emergencia.objects.filter(
                paciente=paciente).order_by('paciente__apellidos')
            for emergencia in emergencias:
                    if emergencia not in data:
                        data.append(emergencia)
        return data

    def get(self, request, *args, **kwargs):
        return render_to_response(
            'app_emergencia/busquedaCedula.html',
            {
                'get': True,
                'formulario': buscar_por_nombreForm()
            },
            context_instance=RequestContext(request)
        )

    def post(self, request, *args, **kwargs):
        formulario = buscar_por_nombreForm(request.POST)
        nombre = None
        apellido = None
        if formulario.is_valid():
            nombre = formulario.cleaned_data['nombre']
            apellido = formulario.cleaned_data['apellido']

        return render_to_response(
            'app_emergencia/busquedaCedula.html',
            {
                'lista': self.get_data(nombre=nombre, apellido=apellido),
                'formulario': formulario,
            },
            context_instance=RequestContext(request)
        )


class TriageView(generic.FormView):

    form_class = FormularioEvaluacionPaciente
    template_name = 'triage.html'

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = {
        }
        emergencia = get_object_or_404(
            Emergencia,
            id=self.kwargs['id_emergencia']
        )
        triage = Triage.objects.filter(emergencia=emergencia).last()
        if triage is None:
            return initial
        else:
            initial['motivo'] = triage.motivo
            initial['temperatura'] = triage.signos_tmp
            initial['frecuencia_cardiaca'] = triage.signos_fc
            initial['frecuencia_respiratoria'] = triage.signos_fr
            initial['presion_diastolica'] = triage.signos_pa
            initial['presion_sistolica'] = triage.signos_pb
            initial['saturacion_oxigeno'] = triage.signos_saod
            initial['avpu'] = triage.signos_avpu
            initial['intensidad_dolor'] = triage.signos_dolor
            initial['ingreso'] = triage.ingreso
        return initial

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        emergencia = get_object_or_404(
            Emergencia,
            id=self.kwargs['id_emergencia']
        )
        try:
            medico = Usuario.objects.get(username=request.user)
        except:
            messages.add_message(
                request,
                messages.ERROR,
                'No tiene permisos para \
                ver esta pagina',
                extra_tags='danger'
            )
            return HttpResponseRedirect('/')
        if not ((medico.tipo == "1") or (medico.tipo == "2")):
            messages.add_message(
                request,
                messages.ERROR,
                'No tiene permisos para \
                ver esta pagina',
                extra_tags='danger'
            )
            return HttpResponseRedirect('/')
        return self.render_to_response(
            self.get_context_data(
                form=form,
                get=True,
                idE=emergencia.id,
            )
        )

    def form_valid(self, form):
        medico = Usuario.objects.get(username=self.request.user)
        if 'id_emergencia' in self.kwargs:
            emergencia = get_object_or_404(
                Emergencia,
                id=self.kwargs['id_emergencia']
            )
            triage = Triage.objects.filter(emergencia=emergencia).last()
            if triage is None:
                Triage.objects.create(
                    emergencia=emergencia,
                    medico=medico,
                    fecha=form.cleaned_data['fecha'],
                    motivo=form.cleaned_data['motivo'],
                    areaAtencion=form.cleaned_data['areaAtencion'],
                    signos_tmp=form.cleaned_data['temperatura'],
                    signos_fc=form.cleaned_data['frecuencia_cardiaca'],
                    signos_fr=form.cleaned_data['frecuencia_respiratoria'],
                    signos_pa=form.cleaned_data['presion_diastolica'],
                    signos_pb=form.cleaned_data['presion_sistolica'],
                    signos_saod=form.cleaned_data['saturacion_oxigeno'],
                    signos_avpu=form.cleaned_data['avpu'],
                    signos_dolor=form.cleaned_data['intensidad_dolor'],
                    ingreso=form.cleaned_data['ingreso'],
                )
            else:
                triage.medico = medico
                triage.fecha = form.cleaned_data['fecha']
                triage.motivo = form.cleaned_data['motivo']
                triage.ingreso = form.cleaned_data['ingreso']
                triage.areaAtencion = form.cleaned_data['areaAtencion']
                triage.signos_tmp = form.cleaned_data['temperatura']
                triage.signos_fc = form.cleaned_data['frecuencia_cardiaca']
                triage.signos_fr = form.cleaned_data['frecuencia_respiratoria']
                triage.signos_pa = form.cleaned_data['presion_diastolica']
                triage.signos_pb = form.cleaned_data['presion_sistolica']
                triage.signos_saod = form.cleaned_data['saturacion_oxigeno']
                triage.signos_avpu = form.cleaned_data['avpu']
                triage.signos_dolor = form.cleaned_data['intensidad_dolor']
                triage.save()

        return render_to_response(
            self.template_name,
            {
                'form': form,
                'triage': triage,
                'idE': emergencia.id

            },
            context_instance=RequestContext(self.request))

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        emergencia = get_object_or_404(
            Emergencia,
            id=self.kwargs['id_emergencia']
        )
        return self.render_to_response(
            self.get_context_data(
                form=form,
                get=True,
                idE=emergencia.id,
            )
        )


def fetch_resources(uri, rel):
    """
    Callback to allow pisa/reportlab to retrieve Images,Stylesheets, etc.
    `uri` is the href attribute from the html link element.
    `rel` gives a relative path, but it's not used here.

    """
    import os
    from django.conf import settings

    """
    Callback to allow xhtml2pdf/reportlab to retrieve Images,Stylesheets, etc.
    `uri` is the href attribute from the html link element.
    `rel` gives a relative path, but it's not used here.

    """
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT,
                            uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT,
                            uri.replace(settings.STATIC_URL, ""))
    else:
        path = os.path.join(settings.STATIC_ROOT,
                            uri.replace(settings.STATIC_URL, ""))

        if not os.path.isfile(path):
            path = os.path.join(settings.MEDIA_ROOT,
                                uri.replace(settings.MEDIA_URL, ""))

            if not os.path.isfile(path):
                raise UnsupportedMediaPathException(
                    'media urls must start with %s or %s' % (
                        settings.MEDIA_ROOT, settings.STATIC_ROOT))

    return path


class triagePDF(generic.DetailView):
    context_object_name = 'triage'
    model = Triage
    template_name = 'app_emergencia/triage_pdf.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        from xhtml2pdf import pisa
        from django.template.loader import get_template
        import StringIO
        from django.template import loader, Context

        template = get_template(self.template_name)
        ctx = Context({'triage': context['triage']})
        body_tpl = loader.get_template(self.template_name)
        html = body_tpl.render(ctx)
        # html = template.render(ctx)
        result = StringIO.StringIO()
        pdf = pisa.pisaDocument(
            StringIO.StringIO(html.encode("UTF-8")),
            dest=result,
            encoding='UTF-8',
            link_callback=fetch_resources
            )

        if not pdf.err:
            response = HttpResponse(
                result.getvalue(),
                content_type='application/pdf')

        return response
        # Se deja esta linea para poder trabajar el HTML
        # en caso de ser necesario
        return self.render_to_response(context)
