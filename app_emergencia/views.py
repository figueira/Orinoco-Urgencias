  # -*- encoding: utf-8 -*-
# coding: latin1

# Manejo de Sesion
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Formularios
from django.core.context_processors import csrf
from django.template import RequestContext

# General HTML
from django.shortcuts import render_to_response, redirect, get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect

# Manejo de Informacion de esta aplicacion
from django.utils.timezone import utc
from datetime import datetime, date, timedelta
from models import *
from forms import *
from app_usuario.forms import *

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
#Imports Atencion
import ho.pisa as pisa
import cStringIO as StringIO
import cgi
import json
from django.template.loader import render_to_string
from app_enfermedad.models import *
from app_paciente.models import *
from itertools import izip
######################################################

    
# Cantidad de segundos en 1,2,..,6 horas
# hora_en_segundos[0] -> Segundos en 0 horas
# hora_en_segundos[1] -> Segundos en 1 hora
# .
# .
# .
# hora_en_segundos[6] -> Segundos en 6 horas
hora_en_segundos = [0,3600,7200,10800,14400,18000,21600] 

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
                pacientes = Paciente.objects.filter(cedula__icontains=p_cedula)
                if len(pacientes) > 0:
                    for p in pacientes:
                        resultados.append(p)
            else:
                print "Se busco por NO cedula"
                print "nombres:"+p_nombres+"y apellidos "+p_apellidos
                if len(p_nombres) > 0 and len(p_apellidos) > 0:
                    print "Se busco por Nombre y Apellido"
                    pacientes = Paciente.objects.filter(nombres__icontains=p_nombres,apellidos__icontains=p_apellidos)
                    if len(pacientes) > 0:
                        for p in pacientes:
                            resultados.append(p)
                elif len(p_apellidos) == 0:
                    print "Se busco por Nombre"
                    pacientes = Paciente.objects.filter(nombres__icontains=p_nombres)
                    if pacientes:
                        for p in pacientes:
                            resultados.append(p)
                elif len(p_nombres) == 0:
                    print "Se busco por Apellido"
                    pacientes = Paciente.objects.filter(apellidos__icontains=p_apellidos)
                    if pacientes:
                        for p in pacientes:
                            resultados.append(p)
            lista = []
            for p in resultados:
                emergencias = Emergencia.objects.filter(paciente=p)
                for e in emergencias:
                    lista.append(e)
                    
        info = {'form':form,'lista':lista,'titulo':titulo}
        return render_to_response('listaB.html',info,context_instance=RequestContext(request))
    else:
        busqueda = BuscarEmergenciaForm()
    
    info = {'form':form,'busqueda':busqueda,'titulo':titulo,'boton':boton}
    return render_to_response('busqueda.html',info,context_instance=RequestContext(request))

#   Busca en la base de datos las emergencias y los 
#   cubiculos que seran utilizados en la vista lista.hmtl
#
def emergencia_listar_todas(request, mensaje = ''):
  emergencias = Emergencia.objects.filter(hora_egreso = None) \
                                  .order_by('hora_ingreso')
  cubiculos = Cubiculo.objects.all()

  form = IniciarSesionForm()
  titulo = "Área de emergencias"
  buscar_enfermedad = False
  info = { 'emergencias': emergencias,
           'cubiculos': cubiculos,
           'form': form, 
           'mensaje': mensaje,
           'titulo': titulo, 
           'buscadorDeEnfermedad': buscar_enfermedad }
  return render(request,
                'lista.html', 
                info)

def emergencia_listar_triage(request):
  # En el area de triage se listan todos los pacientes que no tienen cubiculo
  # asignado y no han sido egresados
  emergencias = Emergencia.objects \
                          .filter(asignarcub__isnull = True, \
                                  hora_egreso = None) \
                          .distinct() \
                          .order_by('hora_ingreso')
  form = IniciarSesionForm()
  titulo = "Área de triage"
  buscar_enfermedad = False
  cubiculos = Cubiculo.objects.all()
  info = {'emergencias': emergencias, 
          'form': form, 
          'titulo': titulo,
          'cubiculos': cubiculos,
          'buscadorDeEnfermedad': buscar_enfermedad }
  return render_to_response('lista.html',
                            info,
                            context_instance = RequestContext(request))

def emergencia_listar_sinclasificar(request):    
  emergencias = Emergencia.objects.filter(hora_egreso = None,
                                          triage__isnull = True) \
                                  .order_by('hora_ingreso')
  form = IniciarSesionForm()
  titulo = "Sin clasificar"
  buscar_enfermedad = False
  cubiculos = Cubiculo.objects.all()
  info = {'emergencias': emergencias, 
          'form': form, 
          'titulo': titulo,
          'cubiculos': cubiculos,
          'buscadorDeEnfermedad': buscar_enfermedad }
  return render_to_response('lista.html',
                            info,
                            context_instance=RequestContext(request))

def emergencia_listar_clasificados(request):
  emergencias = Emergencia.objects \
                          .filter(hora_egreso = None,
                                  triage__isnull = False,
                                  atencion__isnull = True) \
                          .distinct() \
                          .order_by('hora_ingreso')
  form = IniciarSesionForm()
  titulo = "Clasificados"
  buscar_enfermedad = False
  cubiculos = Cubiculo.objects.all()
  info = {'emergencias': emergencias,
          'form': form, 
          'titulo': titulo,
          'cubiculos': cubiculos,
          'buscadorDeEnfermedad': buscar_enfermedad }
  return render_to_response('lista.html',
                            info,
                            context_instance = RequestContext(request))

def emergencia_listar_atencion(request, mensaje):
  emergencias = Emergencia.objects.filter(hora_egreso = None,
                                          atencion__isnull = False) \
                                  .distinct() \
                                  .order_by('hora_ingreso')
  form = IniciarSesionForm()
  titulo = "Atendidos"
  buscar_enfermedad = True
  cubiculos = Cubiculo.objects.all()
  info = {'emergencias': emergencias, 
          'form': form, 
          'titulo': titulo, 
          'cubiculos': cubiculos,
          'mensaje': mensaje,
          'buscadorDeEnfermedad': buscar_enfermedad }
  return render_to_response('lista.html', 
                            info, 
                            context_instance = RequestContext(request))

def emergencia_listar_observacion(request, mensaje = ''):
  emergencias = Emergencia \
                .objects \
                .filter(hora_egreso = None,
                        asignarcub__cubiculo__area__nombre__icontains =
                          'observación') \
                .order_by('hora_ingreso')
  form = IniciarSesionForm()
  titulo = "Observación"
  buscarEnfermedad = True
  cubiculos = Cubiculo.objects.all()
  info = {'emergencias': emergencias,
          'form': form,
          'titulo': titulo,
          'cubiculos': cubiculos,
          'mensaje': mensaje,
          'buscadorDeEnfermedad': buscarEnfermedad }
  return render_to_response('lista.html',
                            info,
                            context_instance = RequestContext(request))

def emergencia_listar_ambulatoria(request, mensaje = ''):
  emergencias = Emergencia \
                .objects \
                .filter(hora_egreso = None,
                        asignarcub__cubiculo__area__nombre__icontains =
                          'ambulatoria') \
                .order_by('hora_ingreso')
  form = IniciarSesionForm()
  titulo = "Ambulatorio"
  buscar_enfermedad = True
  cubiculos = Cubiculo.objects.all()
  info = {'emergencias': emergencias,
          'form': form,
          'titulo': titulo,
          'cubiculos': cubiculos,
          'mensaje': mensaje,
          'buscadorDeEnfermedad': buscar_enfermedad }
  return render_to_response('lista.html',
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
      p_nombres = pcd['nombres']
      p_apellidos = pcd['apellidos']
      p_sexo = pcd['sexo']
      p_fecha_nacimiento = pcd['fecha_nacimiento']
      prueba = Paciente.objects.filter(cedula = p_cedula)
      if len(prueba) == 0:
        p = Paciente(cedula = p_cedula,
                     nombres = p_nombres,
                     apellidos = p_apellidos,
                     sexo = p_sexo,
                     fecha_nacimiento = p_fecha_nacimiento,
                     tlf_cel = "",
                     email = "",
                     direccion = "",
                     tlf_casa = "",
                     contacto_rel = 11,
                     contacto_nom = "",
                     contacto_tlf = "")
        p.save()
      else:
        p = prueba[0]

      e_activa = len(Emergencia.objects
                               .filter(paciente = p)
                               .filter(hora_egreso__isnull = True))
      if e_activa == 0:
        e_ingreso = Usuario.objects.get(username = request.user)
        e_responsable = e_ingreso
        e_horaIngreso = pcd['ingreso']
        e_horaIngresoReal = datetime.now()
        e  =  Emergencia(paciente = p,
                       responsable = e_responsable,
                       ingreso = e_ingreso,
                       hora_ingreso = e_horaIngreso,
                       hora_ingresoReal = e_horaIngresoReal,
                       hora_egreso = None)
        e.save()
        espe = get_object_or_404(Espera,nombre = 'Ubicacion')
        espera1 = EsperaEmergencia(espera = espe,emergencia = e,estado = '0')
        espera1.save()
        return redirect('/emergencia/listar/todas')
      else:
        msj_tipo = "error"
        msj_info = "Ya este usuario esta en una emergencia. No puede ingresar a un usuario 2 veces a la emergencia"
    info = {'form':form,'msj_tipo':msj_tipo,'msj_info':msj_info}
    return render_to_response('agregarPaciente.html',info,context_instance=RequestContext(request))
  form = AgregarEmergenciaForm()
  info = {'form':form}
  return render_to_response('agregarPaciente.html',info,context_instance=RequestContext(request))

@login_required(login_url='/')
def emergencia_agrega_emer(request,id_emergencia):
    emergencia = get_object_or_404(Emergencia,id=id_emergencia)
    p = Paciente.objects.filter(id=emergencia.paciente.id)
    e_activa = len(Emergencia.objects.filter(paciente=p[0]).filter(hora_egreso__isnull=True))
    if e_activa == 0:
        e_ingreso = Usuario.objects.get(username=request.user)
        e_responsable= e_ingreso
        e_horaIngreso = datetime.now()
        e_horaIngresoReal = datetime.now()
        e = Emergencia(paciente=p[0],responsable=e_responsable,ingreso=e_ingreso,hora_ingreso=e_horaIngreso,hora_ingresoReal=e_horaIngresoReal,hora_egreso=None)
        e.save()
        espe = get_object_or_404(Espera,nombre = 'Ubicacion')
        espera1 = EsperaEmergencia(espera = espe,emergencia = e,estado = '0')
        espera1.save()
        print "Creando nueva emergencia objeto creado: ",e
        return redirect('/emergencia/listar/todas')
    else:
        msj_tipo = "error"
        msj_info = "Ya este usuario esta en una emergencia. No puede ingresar a un usuario 2 veces a la emergencia"
        # mensaje = "Ya este usuario esta en una emergencia. No puede ingresar a un usuario 2 veces a la emergencia"
        # print " ya este paciente tiene una emergencia activa"
        # info = {'mensaje':mensaje}
        # return render_to_response('listaB.html',info,context_instance=RequestContext(request))
        return redirect('/emergencia/listar/todas')
        

@login_required(login_url='/')
def emergencia_darAlta(request,idE):
  emergencia = get_object_or_404(Emergencia,id=idE)
  medico = Usuario.objects.get(username=request.user)
  if (medico.tipo == "1"):
    if request.method == 'POST':
      form = darAlta(request.POST)
      if form.is_valid():
        # Iniciar una transaccion para asegurar que las dos operaciones se
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
          asigCA = AsignarCub.objects.filter(emergencia = emergencia)
          if asigCA:
            asigCA.delete()
          else:
            print "Dando de alta sin cubiculo asignado"

          # Si habia alguna espera activa, marcarla como atendida
          esperas = EsperaEmergencia.objects.filter(emergencia = emergencia,
                                                    hora_fin = None)
          for espera in esperas:
            espera.hora_fin = f_darAlta
            espera.save()

      else:
        info = {'form':form,'emergencia':emergencia}
        return render_to_response('darAlta.html',info,context_instance = RequestContext(request))
    else:
      form = darAlta()
      info = {'form':form,'emergencia':emergencia}
      return render_to_response('darAlta.html',info,context_instance = RequestContext(request))  
  return redirect("/emergencia/listar/todas")

@login_required(login_url='/')
def emergencia_aplicarTriage(request, idE, vTriage):
  emergencia = get_object_or_404(Emergencia, id = idE)
  paciente = emergencia.paciente
  medico = Usuario.objects.get(username = request.user)
  if ((medico.tipo == "1") or (medico.tipo == "2")):
    fechaReal  = datetime.now()
    motivo = Motivo.objects.get(nombre__startswith = " Ingreso")
    area = AreaEmergencia.objects.get(nombre__startswith = " Ingreso")
    recursos = 2
    if (vTriage == ''):
      # El paciente debe ser evaluado para asignarle un triage
      if((paciente.signos_tmp < 37 or 38.4 < paciente.signos_tmp) or
         (paciente.signos_fc < 60 or 100 < paciente.signos_fc) or
         (paciente.signos_fr < 14 or 20 < paciente.signos_fr) or
         (paciente.signos_pa < 60 or 89 < paciente.signos_pa) or
         (paciente.signos_pb < 100 or 139 < paciente.signos_pb) or
         (paciente.signos_saod < 95 or 100 < paciente.signos_saod)):
        vTriage = 2
      else:
        vTriage = 3

    if (vTriage == 1):
      atencion = True
    elif (vTriage == 2):
      atencion = False
      esperar = False
    else:
      if (vTriage == 4):
        recursos = 1
      elif (vTriage == 5):
        recursos = 0
      atencion = False
      esperar = True
    t = Triage(emergencia = emergencia,
               medico = medico,
               fecha = fechaReal,
               motivo = motivo,
               atencion = atencion,
               esperar = esperar,
               areaAtencion = area,
               recursos = recursos,
               nivel = vTriage)
    print 'Triage asignado: ' + str(vTriage)
    t.save()
    return redirect('/emergencia/listar/todas')
  return redirect("/")

@login_required(login_url='/')
def emergencia_calcular_triage(request, idE, triage_asignado):
  mensaje = ""
  form = FormularioEvaluacionPaciente()
  info = {'form': form, 'idE': idE, 'triage_asignado': triage_asignado}
  return render_to_response('calcularTriage.html',
                            info,
                            context_instance = RequestContext(request))

def estadisticas_prueba():
#    triages = Triage.objects.filter(fecha__year=ano).filter(fecha__month=mes).values('nivel').annotate(Count('nivel')).order_by('nivel')
#    triages = [[i['nivel'],i['nivel__count']] for i in triages]
#    triagesBien = [[1,0],[2,0],[3,0],[4,0],[5,0]]
#    for i in triages:
#      triagesBien[i['nivel']] = i['count']
    triages = Triage.objects.all().values('nivel').annotate(Count('nivel')).order_by('nivel')
    triages = [[i['nivel'],i['nivel__count']] for i in triages]
    triagesBien = [0,0,0,0,0]
    for i in triages:
        triagesBien[i[0]-1] = i[1]
    triages = []
    for i in range(5):
      triages.append([(i+1),triagesBien[i]])
    return triages

def obtener_imagenes():
  objetos_causas_de_espera = Espera.objects.all()
  imagenes = []
  for espera in objetos_causas_de_espera:
    imagenes.append(espera.url_imagen)
  return imagenes

def ordenar_por_causas(diccionario_de_causas):
  resultado = sorted(diccionario_de_causas.items(), key = lambda t: t[0])
  return resultado

def ordenar_por_color(diccionario_de_causas):
  resultado = [('Verde', diccionario_de_causas['Verde']),
	       ('Amarillo', diccionario_de_causas['Amarillo']),
	       ('Rojo', diccionario_de_causas['Rojo']),
	       ('Negro', diccionario_de_causas['Negro'])]
  return resultado

def ordenar_por_color_transicion(diccionario_de_causas):
  resultado = [('Amarillo', diccionario_de_causas['Amarillo']),
	       ('Rojo', diccionario_de_causas['Rojo']),
	       ('Negro', diccionario_de_causas['Negro'])]
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
      causas_de_espera[causa.nombre] = ([0,0,0,0], causa.url_imagen())
      causas_transicion[causa.nombre] = ([0,0,0], causa.url_imagen())
      
    for emergencia in emergencias:
      espera_emergencias = EsperaEmergencia.objects.filter(emergencia=emergencia)
      hora_inicio_emergencia = emergencia.hora_ingreso
      for espera_emergencia in espera_emergencias:
        causa = espera_emergencia.espera.nombre
        if espera_emergencia.hora_fin == None:
          continue
        tiempo_espera = (espera_emergencia.hora_fin -
                          espera_emergencia.hora_comienzo).seconds
        if tiempo_espera < hora_en_segundos[2]:
          grupo = 0
        elif hora_en_segundos[2] <= tiempo_espera and \
             tiempo_espera < hora_en_segundos[4]:
          grupo = 1
        elif hora_en_segundos[4] <= tiempo_espera and \
             tiempo_espera < hora_en_segundos[6]:
          grupo = 2
        else:
          grupo = 3
          
        dif_inicio = (espera_emergencia.hora_comienzo - hora_inicio_emergencia).seconds
        dif_fin = (espera_emergencia.hora_fin - hora_inicio_emergencia).seconds
        
        if dif_inicio < hora_en_segundos[2]:
          grupo_trans_inicio = -1
        elif hora_en_segundos[2] <= dif_inicio and \
             dif_inicio < hora_en_segundos[4]:
          grupo_trans_inicio = 0
        elif hora_en_segundos[4] <= dif_inicio and \
             dif_inicio < hora_en_segundos[6]:
          grupo_trans_inicio = 1
        else:
          grupo_trans_inicio = 2
          
        if dif_fin < hora_en_segundos[2]:
          grupo_trans_fin = -1
        elif hora_en_segundos[2] <= dif_fin and dif_fin < hora_en_segundos[4]:
          grupo_trans_fin = 0
        elif hora_en_segundos[4] <= dif_fin and dif_fin < hora_en_segundos[6]:
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
      causas_invertidas.append((color,[]))
     
    aux = [x[0] for x in causas_invertidas]
    for causa in intermedio:
      (valores,img) = causa[1]
      for i in range(0,len(colores)):
        causas_invertidas[aux.index(colores[i])][1].append((causa[0],valores[i]))
    return causas_invertidas


def estadisticas_per(request,dia,mes,anho,dia2,mes2,anho2):
    # Datos generales
    fecha_inicio = date(int(anho),int(mes),int(dia))
    fecha_fin = date(int(anho2),int(mes2),int(dia2))
    siguiente_semana = fecha_fin + timedelta(days=7)
    ingresos_emergencia = Emergencia.objects.filter(
                            hora_ingreso__range=[fecha_inicio,fecha_fin])
    egresos_emergencia = Emergencia.objects.filter(
                            hora_egreso__range=[fecha_inicio,fecha_fin])
    
    # Cantidad de emergencias por duracion
    # horas[0] -> 0 a 2 horas
    # horas[1] -> 2 a 4 horas
    # horas[2] -> 4 a 6 horas
    # horas[3] -> 6 o + horas
    horas = [0,0,0,0]

    
    # Emergencias por duracion
    # emergencias_por_horas[0] -> 0 a 2 horas
    # emergencias_por_horas[1] -> 2 a 4 horas
    # emergencias_por_horas[2] -> 4 a 6 horas
    # emergencias_por_horas[3] -> 6 o + horas
    emergencias_por_horas = [[],[],[],[]]
    
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
    causas = [('General', ordenar_por_causas(causas_pacientes_total)),
	      ('Verde', ordenar_por_causas(causas_pacientes_en_verde)),
	      ('Amarillo', ordenar_por_causas(causas_pacientes_en_amarillo)),
	      ('Rojo', ordenar_por_causas(causas_pacientes_en_rojo)),
	      ('Negro', ordenar_por_causas(causas_pacientes_en_negro))]
    causas_transicion = [('Amarillo', ordenar_por_causas(causas_transicion_amarillo)),
			 ('Rojo', ordenar_por_causas(causas_transicion_rojo)),
			 ('Negro', ordenar_por_causas(causas_transicion_negro))]
    
    imaganes = obtener_imagenes()
    
    lista_auxiliar = [causas_pacientes_en_verde,\
      causas_pacientes_en_amarillo, causas_pacientes_en_rojo, \
	causas_pacientes_en_negro]
    lista_auxiliar_transicion = [causas_transicion_amarillo, \
      causas_transicion_rojo, causas_transicion_negro]
    
    colores = ['Verde','Amarillo','Rojo','Negro']
    colores_transicion = ['Amarillo','Rojo','Negro']
    causas_invertidas = []
    for x, y in zip(lista_auxiliar, colores):
      causas_invertidas.append((y,invertir_orden_de_diccionario(x,colores)))
    causas_transicion_invertidas = []
    for x, y in zip(lista_auxiliar_transicion, colores_transicion):
      causas_transicion_invertidas.append((y,\
	  invertir_orden_de_diccionario(x,colores_transicion)))
    
    causas_invertidas=[('General',invertir_orden_de_diccionario(\
	causas_pacientes_total,colores))] + causas_invertidas
    # Resultados de los Triages
    triages = Triage.objects.filter(fecha__range=[fecha_inicio,fecha_fin]) \
              .values('nivel').annotate(Count('nivel')).order_by('nivel')
    triages = [[i['nivel'],i['nivel__count']] for i in triages]
    triagesBien = [0,0,0,0,0]
    for i in triages:
        triagesBien[i[0]-1] = i[1]
    triages = []
    for i in range(5):
      triages.append([(i+1),triagesBien[i]])
    egresos = [['Total',total_egresos],['Verde (0 a 2 horas)',horas[0]],
                ['Amarillo (2 a 4 horas)',horas[1]],['Rojo (4 a 6 horas)',horas[2]],
                ['Negro (6 o + horas)',horas[3]]
              ]
    
    prueba = invertir_orden_de_diccionario(lista_auxiliar[3],colores)
    
    info = {'triages':triages,'fecha':date.today(),'inicio':fecha_inicio,
            'fin':fecha_fin-timedelta(days=1),'sig':siguiente_semana,
             'total_ingresos':len(ingresos_emergencia),
             'total_egresos':total_egresos,
             'egresos':egresos, 'emergencias':emergencias_por_horas,
             'causas':causas, 'imagenes': imaganes,
             'causas_transicion': causas_transicion,
             'causas_invertidas': causas_invertidas,
             'causas_transicion_invertidas': causas_transicion_invertidas,
             'colores': colores,
             'colores_transicion': colores_transicion,
             'lista_auxiliar': lista_auxiliar,
             'prueba': prueba
            }
    return render_to_response('estadisticas.html',info,
                              context_instance=RequestContext(request))

def estadisticas_sem(request,dia,mes,anho):
    fecha_fin = datetime(int(anho),int(mes),int(dia))
    fecha_inicio = fecha_fin - timedelta(weeks=1)
    return redirect('/estadisticas/' + str(fecha_inicio.day) + '-' + 
                      str(fecha_inicio.month) + '-' + str(fecha_inicio.year) +
                      '/' + dia + '-' + mes + '-' + anho)
    
def estadisticas(request):
    hoy = datetime.today()
    return redirect('/estadisticas/' + str(hoy.day) + '-' + str(hoy.month) +
                    '-' + str(hoy.year))


#########################################################
#                                                       #
#          Views para Casos de Uso de Esperas           #
#                                                       #
#########################################################
def emergencia_espera_mantener(request,id_emergencia):
    emer   = get_object_or_404(Emergencia,id=id_emergencia)
    emer.fecha_Esp_act = datetime.now()
    emer.save()
    return HttpResponse()

# Método que realiza la asociación en la base de datos de una espera a una
# emergencia. Devuelve una respuesta en JSON con el identificador de la entidad
# creada
def emergencia_agregar_espera(request, id_emergencia, id_espera):
    emergencia = get_object_or_404(Emergencia, id = id_emergencia)
    emergencia.fecha_Esp_act = datetime.now()
    emergencia.save()
    espera = get_object_or_404(Espera, id = id_espera)
    espera_emergencia = EsperaEmergencia(emergencia = emergencia,
                                         espera = espera,
                                         estado = '0')
    espera_emergencia.save()
    return HttpResponse(json.dumps(espera_emergencia.id),
                        content_type='application/json')

def emergencia_eliminar_espera_emergencia(request, id_espera_emergencia):
    espera_emergencia = get_object_or_404(EsperaEmergencia,
                                          id = id_espera_emergencia)
    emergencia = espera_emergencia.emergencia
    emergencia.fecha_Esp_act = datetime.now()
    emergencia.save()
    espera_emergencia.delete() 
    return HttpResponse()

def emergencia_espera_estado(request,id_emergencia,id_espera,espera):
    emer               = get_object_or_404(Emergencia,id=id_emergencia)
    emer.fecha_Esp_act = datetime.now()
    emer.save()
    espe               = get_object_or_404(Espera,id=id_espera)
    espera1            = EsperaEmergencia.objects.get(espera=espe,emergencia=emer)
    espera1.estado     = str(espera)
    espera1.save() 
    return HttpResponse()

def emergencia_espera_asignadasCheck(request,id_emergencia):
    emer = get_object_or_404(Emergencia,id=id_emergencia)
    esperasEmer = EsperaEmergencia.objects.filter(emergencia=emer)
    esperasEmer = [str(i.estado) for i in esperasEmer]
    esp = ""
    for i in esperasEmer:
        esp = esp+i+","
    return HttpResponse(esp)

def emergencia_espera_id(request,id_emergencia):
    esperas = EsperaEmergencia.objects.filter(emergencia__id=id_emergencia)
    esperas = [str(i.espera.id) for i in esperas]
    esp = ""
    for i in esperas:
        esp = esp+i+","
    return HttpResponse(esp)

def emergencia_espera_idN(request,id_emergencia):
    emer = get_object_or_404(Emergencia,id=id_emergencia)
    esperasEmer = EsperaEmergencia.objects.filter(emergencia=emer)
    esperasEmer = [str(i.espera.id) for i in esperasEmer]
    esperas     = Espera.objects.filter()
    esperas     = [str(i.id) for i in esperas ]
    for EspEmer in esperasEmer:
        esperas.remove(EspEmer)
    esp = ""
    for i in esperas:
        esp = esp+i+","
    return HttpResponse(esp)

# Se agrega a la base de datos la fechay hora en que se marco check (finalizo) 
# para una causa de espera para una emergencia 
#
def emergencia_espera_finalizada(request,id_espera_emergencia):
    espera_emergencia = EsperaEmergencia.objects.get(id = id_espera_emergencia)
    espera_emergencia.hora_fin = datetime.now()
    espera_emergencia.save() 
    return HttpResponse('')

#########################################################
#                                                       #
#             Guardar/ Actualizar Cubiculo              #
#                                                       #
#########################################################

#------------------------------------------ Funciones para agregar un cubiculo
def emergencia_guardar_cubi(request, id_emergencia, accion):
  emergencia = get_object_or_404(Emergencia, id = id_emergencia)

  id_cubiculo = request.GET['id_cubiculo']
  if id_cubiculo == '':
    cubiculo = None
  else:
    cubiculo  = get_object_or_404(Cubiculo, id = id_cubiculo)

  if (cubiculo != None) and (cubiculo.esta_asignado()):
    mensaje = "Error: El cubiculo " + cubiculo.nombre + \
              " esta asignado a otro paciente"
  else:
    tiene_cubiculo = AsignarCub.objects.filter(emergencia = emergencia) \
                                       .count() > 0
    if (cubiculo != None) and (not tiene_cubiculo):
      emergencia.fecha_Esp_act = datetime.now()
      emergencia.save()

      # Actualizar la causa de espera por ubicacion
      espera = get_object_or_404(Espera, nombre = 'Ubicacion')
      espera_emergencia = EsperaEmergencia.objects \
                                          .filter(espera = espera,
                                                  emergencia = emergencia) \
                                          .update(hora_fin = datetime.now())

      triage = Triage.objects.filter(emergencia = id_emergencia) \
                             .order_by("-fechaReal")

      triage = triage[0]
      atencion = Atencion.objects.create(emergencia = emergencia,
                                         medico = emergencia.responsable,
                                         fecha = datetime.now(),
                                         fechaReal = datetime.now(),
                                         area_atencion = triage.areaAtencion.id)

      # Aqui se garantiza que el 'cubiculo' no va a ser None, puesto que se tuvo
      # que haber seleccionado un cubiculo para llegar aqui
      asignacion_cubiculo = AsignarCub.objects.create(emergencia = emergencia,
                                                      cubiculo = cubiculo)
      mensaje = "Logrado: Cubiculo " + cubiculo.nombre + " asignado"
    else:
      # Aqui necesariamente hay un cubiculo asignado
      asignacion_cubiculo = AsignarCub.objects \
                                      .filter(emergencia = emergencia)[0]
      if cubiculo == None:
        # Aqui se pidio no asignar ningun cubiculo
        asignacion_cubiculo.delete()
        mensaje = 'Logrado: Eliminación de asignación de cubículo'
      else:
        asignacion_cubiculo.cubiculo = cubiculo
        asignacion_cubiculo.save()
        mensaje = "Logrado: Cubiculo " + cubiculo.nombre + " actualizado"

    if cubiculo == None:
      return emergencia_listar_todas(request, mensaje = mensaje)
    else:
	  mensaje = ""
    # if re.search('ambulatoria', cubiculo.area.nombre, flags = re.I):
    #    print 'Enviando a ambulatoria'
    #    return emergencia_listar_ambulatoria(request, mensaje = mensaje)
    #  else:
    #    print 'Enviando a observación'
    #    return emergencia_listar_observacion(request, mensaje)

  return emergencia_listar_todas(request, mensaje = mensaje)

#------------------------------------------ Funciones para agregar un cubiculo
def emergencia_tiene_cubiculo(request,id_emergencia):
    emer = get_object_or_404(Emergencia,id=id_emergencia)
    cubi  = request.POST[str(emer.id)+"cub"]
    asic = Cubiculo.objects.filter(asignarcub__cubiculo__nombre = cubi)
    if asic:
        mensaje = "si"
        return HttpResponse(mensaje)
    else:
        mensaje = "no"
        return HttpResponse(mensaje)

#########################################################
#                                                       #
#          Views para Casos de Uso de Atencion          #
#                                                       #
#########################################################

# A cada una le paso el id de emergencia para mantener la 
# informacion constante en el sidebar izquierdo

#----------------------------------------------------- Funciones para generar Pdfs
def generar_pdf(html):
    result = StringIO.StringIO()
    pdf    = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), mimetype='application/pdf')
    return HttpResponse('Error al generar el PDF: %s' % cgi.escape(html))

def emergencia_descarga(request,id_emergencia,tipo_doc):
    emer  = get_object_or_404(Emergencia,id=id_emergencia)
    ingreso = datetime.now()
    atList = Atencion.objects.filter(emergencia=id_emergencia)
    atList2=atList[0]
    diags = EstablecerDiag.objects.filter(atencion=atList2)
    medicamento = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo = "medicamento")
    
    # TERMINAR CONSULTAS PARA INGRESAR AL CONTEXTO
    if tipo_doc == 'historia':
        # Faltan consultas:
        triage = Triage.objects.filter(emergencia=id_emergencia).order_by("-fechaReal")
        triage2=triage[0]
        dieta = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo = "dieta")
        dieta2 = dieta[0]
        enfA = EnfermedadActual.objects.get(atencion=atList[0].id)
        print "Triage en descarga",triage2
        ctx  = {'emergencia':emer,'ingreso':ingreso,'triage':triage2,'atencion':atList2,'enfA':enfA,'diags':diags,'dieta':dieta2,'medicamento':medicamento}
        html = render_to_string('historia_med.html',ctx, context_instance=RequestContext(request))
    
    elif tipo_doc == 'constancia':
        dieta = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo = "dieta")
        dieta2 = dieta[0]
        print "Dietas en descarga:",dieta
        print"Medicamcion en descarga",medicamento
        info = {'ingreso':ingreso,'emergencia':emer,'diags':diags,'dieta':dieta2,'medicamento':medicamento}
        html = render_to_string('const_asist.html',info, context_instance=RequestContext(request))
    
    elif tipo_doc == 'reportInd':
        indicaciones = Asignar.objects.filter(emergencia = id_emergencia)
        ctx  = {'emergencia':emer,'indicaciones':indicaciones,'ingreso':ingreso}
        html = render_to_string('reporte_ind.html',ctx, context_instance=RequestContext(request))
    return generar_pdf(html)

#----------------------------------Gestion de Enfermedad Actual
@login_required(login_url='/')
def emergencia_enfermedad_actual(request,id_emergencia):
    emer = get_object_or_404(Emergencia,id=id_emergencia)
    paci = Paciente.objects.filter(emergencia__id=id_emergencia)
    paci = paci[0]
    triage = Triage.objects.filter(emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    mensaje = ""
    ya=""
    atList = Atencion.objects.filter(emergencia=id_emergencia)
    
    # if len(atList) == 0:
    #     atencion = Atencion(emergencia=emer,medico=emer.responsable,fecha=datetime.now(),fechaReal=datetime.now(),area_atencion=triage.areaAtencion)
    #     atencion.save()
    #     atList = Atencion.objects.filter(emergencia=id_emergencia)
    
    if request.method == 'POST':
        form = AgregarEnfActual(request.POST)
        if form.is_valid():
            pcd = form.cleaned_data
            narrativa          = pcd['narrativa']
            # Busco si ya existe una narrativa para esa indicacion
            enfA = EnfermedadActual.objects.filter(atencion=atList[0].id)
            # Si existe, la sobreescribo
            if enfA:
                enfA[0].narrativa=narrativa
                enfA[0].save()
                
            else:
                enfA = EnfermedadActual(atencion=atList[0],narrativa=narrativa)
                enfA.save()
                # mensaje = " Agregado Exitosamente: "+enfA.narrativa
                mensaje = " Agregado Exitosamente "
                info = {'form':form,'emergencia':emer,'triage':triage, 'mensaje':mensaje, 'ya':ya}
                return render_to_response('atencion_enfA.html',info,context_instance=RequestContext(request))

            # mensaje = "Actualizado Exitosamente: "+enfA[0].narrativa
            mensaje = "Actualizado Exitosamente "
            info = {'form':form,'emergencia':emer,'triage':triage, 'mensaje':mensaje,'ya':ya}
            return render_to_response('atencion_enfA.html',info,context_instance=RequestContext(request))

    enfa= EnfermedadActual.objects.filter(atencion=atList[0])
    
    if enfa:
        mensaje = "Ya se ha establecido una narrativa para este paciente"
        form = AgregarEnfActual(initial={'narrativa':enfa[0].narrativa})
        ya="si"
    else:
        form = AgregarEnfActual()
    
    info = {'form':form,'emergencia':emer,'triage':triage, 'mensaje':mensaje, 'ya':ya}
    return render_to_response('atencion_enfA.html',info,context_instance=RequestContext(request))

# --- RGV

@login_required(login_url='/')
def emergencia_atencion(request,id_emergencia,tipo):
    emer   = get_object_or_404(Emergencia,id=id_emergencia)
    triage = Triage.objects.filter(emergencia=id_emergencia).order_by("-fechaReal")
    #aqui cambie cosas atte Carla
    if len(triage) != 0:
      triage = triage[0]
      ctx    = {'emergencia':emer,'triage':triage}

      paci = Paciente.objects.filter(emergencia__id=id_emergencia)
      paci = paci[0]
      atList = Atencion.objects.filter(emergencia=id_emergencia)
      
      if len(atList) == 0:
          atencion = Atencion(emergencia=emer,medico=emer.responsable,fecha=datetime.now(),fechaReal=datetime.now(),area_atencion=triage.areaAtencion_id)
          atencion.save()
          atList = Atencion.objects.filter(emergencia=id_emergencia)

      if tipo == "listado":
          return redirect('/emergencia/listar/atencion')
      elif tipo == "historia":
          return render_to_response('atencion.html',ctx,context_instance=RequestContext(request))
    else:
      if tipo == "listado":
          return redirect('/emergencia/listar/atencion')
      elif tipo == "historia":
          ctx = {'emergencia':emer,'triage': None}
          return render_to_response('atencion.html',ctx,context_instance=RequestContext(request))


def emergencia_antecedentes_agregar(request,id_emergencia,tipo_ant):
    emer    = get_object_or_404(Emergencia,id=id_emergencia)
    paci    = Paciente.objects.get(emergencia__id=id_emergencia)
    triage  = Triage.objects.filter(emergencia=id_emergencia).order_by("-fechaReal")
    triage  = triage[0]
    if request.method == 'POST':
        nombres  = request.POST.getlist('nuevoNombre')
        fechas   = request.POST.getlist('nuevoFecha')
        atributo = request.POST.getlist('nuevoAtributo3')
        for i in range(len(nombres)-1): 
            ant       = Antecedente(tipo=tipo_ant,nombre=nombres[i])
            ant.save()
            pertenece = Pertenencia(paciente=paci,antecedente=ant)
            pertenece.save()
            if tipo_ant =='medica' or tipo_ant =='quirurgica':                
                fecha = Fecha(fecha=int(fechas[i]),pertenencia=pertenece) 
                fecha.save()
                if tipo_ant == 'medica':
                    tratamiento = Tratamiento(nombre=atributo[i])
                    tratamiento.save()
                    trataPerte  = TratamientoPertenencia(pertenencia=pertenece,tratamiento=tratamiento)
                    trataPerte.save() 
                if tipo_ant == 'quirurgica':
                    lugar      = Lugar(nombre=atributo[i])
                    lugar.save()
                    lugarperte = LugarPertenencia(lugar=lugar,pertenencia=pertenece)
                    lugarperte.save()
    pertenece = Pertenencia.objects.filter(paciente=paci,antecedente__tipo=tipo_ant)
    ctx = {'emergencia':emer,'triage':triage,'pertenece':pertenece,'tipo_ant':tipo_ant}
    return render_to_response('atencion_ant_medica.html',ctx,context_instance=RequestContext(request))


def emergencia_antecedentes_modificar(request,id_emergencia,tipo_ant):
    emer         = get_object_or_404(Emergencia,id=id_emergencia)
    paci         = Paciente.objects.get(emergencia__id=id_emergencia)
    triage       = Triage.objects.filter(emergencia=id_emergencia).order_by("-fechaReal")
    triage       = triage[0]
    antecedentes = Antecedente.objects.filter(pertenencia__paciente=paci,tipo=tipo_ant)
    for ant in antecedentes:
        ant.nombre = request.POST[str(ant.id)+"nombre"]
        if tipo_ant == 'medica' or tipo_ant == 'quirurgica':
            pertenece = Pertenencia.objects.filter(paciente=paci,antecedente=ant)
            if pertenece:
                fecha             = Fecha.objects.get(pertenencia=pertenece[0])
                fecha.fecha       = int(request.POST[str(ant.id)+"fecha"])
                fecha.pertenencia = pertenece[0]
                fecha.save()
            if tipo_ant == 'medica':
                tratamiento = Tratamiento.objects.filter(tratamientopertenencia__pertenencia=pertenece[0])
                if tratamiento:
                    tratamiento[0].nombre = request.POST[str(ant.id)+"atributo3"]
                    tratamiento[0].save()
            if tipo_ant == 'quirurgica':
                lugar = Lugar.objects.filter(lugarpertenencia__pertenencia=pertenece[0])
                if lugar:
                    lugar[0].nombre = request.POST[str(ant.id)+"atributo3"]
                    lugar[0].save()
        ant.save()
    pertenece = Pertenencia.objects.filter(paciente=paci,antecedente__tipo=tipo_ant)
    ctx = {'emergencia':emer,'triage':triage,'pertenece':pertenece,'tipo_ant':tipo_ant}
    return render_to_response('atencion_ant_medica.html',ctx,context_instance=RequestContext(request))

def emergencia_antecedentes_eliminar(request,id_emergencia,tipo_ant):
    emer   = get_object_or_404(Emergencia,id=id_emergencia)
    paci   = Paciente.objects.get(emergencia__id=id_emergencia)
    triage = Triage.objects.filter(emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    antecedentes = Antecedente.objects.filter(pertenencia__paciente=paci,tipo=tipo_ant)
    if request.method == 'POST':
        checkes = request.POST.getlist(u'check')
        for id_ant in checkes:
            ant       = Antecedente(id=id_ant)
            pertenece = Pertenencia.objects.filter(paciente=paci,antecedente_id=id_ant)
            if pertenece:
                fecha  = Fecha.objects.filter(pertenencia=pertenece[0])
                fecha.delete()
                lugarpertence = LugarPertenencia.objects.filter(pertenencia=pertenece[0])
                if lugarpertence:
                    lugarpertence.delete()
                tratamiento = TratamientoPertenencia.objects.filter(pertenencia=pertenece[0])
                if tratamiento:
                    tratamiento.delete() 
            pertenece.delete()
    pertenece = Pertenencia.objects.filter(paciente=paci,antecedente__tipo=tipo_ant)
    ctx = {'emergencia':emer,'triage':triage,'pertenece':pertenece,'tipo_ant':tipo_ant}
    return render_to_response('atencion_ant_medica.html',ctx,context_instance=RequestContext(request))


#----------------------------------Gestion de Antecedentes en area de Atencion
@login_required(login_url='/')
def emergencia_antecedentes(request,id_emergencia):
    emer   = get_object_or_404(Emergencia,id=id_emergencia)
    triage = Triage.objects.filter(emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    ctx    = {'emergencia':emer,'triage':triage}
    return render_to_response('atencion_ant.html',ctx,context_instance=RequestContext(request))

#----------------------------------Gestion de Antecedentes en area de Atencion
@login_required(login_url='/')
def emergencia_antecedentes_tipo(request,id_emergencia,tipo_ant):
    emer         = get_object_or_404(Emergencia,id=id_emergencia)
    paci         = Paciente.objects.get(emergencia__id=id_emergencia)
    triage       = Triage.objects.filter(emergencia=id_emergencia).order_by("-fechaReal")
    triage       = triage[0]
    pertenece    = Pertenencia.objects.filter(paciente=paci,antecedente__tipo=tipo_ant)
    antecedentes = Antecedente.objects.filter(pertenencia__paciente=paci,tipo=tipo_ant)
    ctx = {'emergencia':emer,'triage':triage,'antecedentes':antecedentes,'pertenece':pertenece,'tipo_ant':tipo_ant}
    return render_to_response('atencion_ant_medica.html',ctx,context_instance=RequestContext(request))


#--------------------------------Gestion de Enfermedad (Examen Fisico)
@login_required(login_url='/')
def emergencia_enfermedad(request,id_emergencia):
    emer        = get_object_or_404(Emergencia,id=id_emergencia)
    paci        = Paciente.objects.get(emergencia__id=id_emergencia)
    triage      = Triage.objects.filter(emergencia=id_emergencia).order_by("-fechaReal")
    triage      = triage[0]
    causa       = 0
    atencion    = Atencion.objects.filter(emergencia=id_emergencia)
    aspectos    = Aspecto.objects.filter(parteaspecto__partecuerpo__nombre='CABEZA Y ROSTRO')
    aspectoAten = AspectoAtencion.objects.filter(atencion=atencion[0],aspecto__parteaspecto__partecuerpo__nombre='CABEZA Y ROSTRO')
    ctx = {'emergencia':emer,'triage':triage,'causa':causa}
    if paci.sexo == 1:
        return render_to_response('atencion_Plan.html',ctx,context_instance=RequestContext(request))
    else:
        return render_to_response('atencion_Plan_mujer.html',ctx,context_instance=RequestContext(request))

@login_required(login_url='/')
def emergencia_enfermedad_zonacuerpo(request,id_emergencia,zona_cuerpo):
    emer         = get_object_or_404(Emergencia,id=id_emergencia)
    paci         = Paciente.objects.get(emergencia__id=id_emergencia)
    triage       = Triage.objects.filter(emergencia=id_emergencia).order_by("-fechaReal")
    triage       = triage[0]
    causa        = 0
    atencion     = Atencion.objects.filter(emergencia=id_emergencia)
    partecuerpo  = ParteCuerpo.objects.filter(zonaparte__zonacuerpo__nombre=zona_cuerpo)
    parteaspecto = ParteAspecto.objects.filter(partecuerpo__zonaparte__zonacuerpo__nombre=zona_cuerpo)
    aspectoAten  = AspectoAtencion.objects.filter(atencion=atencion[0],aspecto__parteaspecto__partecuerpo__zonaparte__zonacuerpo__nombre=zona_cuerpo)
    aspectos     = Aspecto.objects.filter(parteaspecto__partecuerpo__zonaparte__zonacuerpo__nombre=zona_cuerpo)
    ctx = {'emergencia':emer,'triage':triage,'causa':causa,'paciente':paci,'partecuerpo':partecuerpo,'parteaspecto':parteaspecto,'aspectoAtencion':aspectoAten,'zona_cuerpo':zona_cuerpo}
    return render_to_response('atencion_Plan_cuerpo.html',ctx,context_instance=RequestContext(request))

@login_required(login_url='/')
def emergencia_enfermedad_partecuerpo(request,id_emergencia,parte_cuerpo):
    emer        = get_object_or_404(Emergencia,id=id_emergencia)
    triage      = Triage.objects.filter(emergencia=id_emergencia).order_by("-fechaReal")
    triage      = triage[0]
    causa       = 0
    atencion    = Atencion.objects.filter(emergencia=id_emergencia)
    atencion    = atencion[0]
    aspectoAten = AspectoAtencion.objects.filter(atencion=atencion,aspecto__parteaspecto__partecuerpo__nombre=parte_cuerpo)
    aspectos    = Aspecto.objects.filter(parteaspecto__partecuerpo__nombre=parte_cuerpo)
    if not(aspectoAten):
        for aspe in aspectos:
            AspeAten = AspectoAtencion(revisado='no',aspecto=aspe,atencion=atencion)
            AspeAten.save()
    aspectoAten = AspectoAtencion.objects.filter(atencion=atencion,aspecto__parteaspecto__partecuerpo__nombre=parte_cuerpo)
    ctx = {'emergencia':emer,'triage':triage,'causa':causa,'aspectoAtencion':aspectoAten,'parte_cuerpo':parte_cuerpo}
    return render_to_response('atencion_Plan_partecuerpo.html',ctx,context_instance=RequestContext(request))

@login_required(login_url='/')
def emergencia_enfermedad_enviarcuerpo(request,id_emergencia,parte_cuerpo):
    emer        = get_object_or_404(Emergencia,id=id_emergencia)
    triage      = Triage.objects.filter(emergencia=id_emergencia).order_by("-fechaReal")
    triage      = triage[0]
    causa       = 0
    atencion    = Atencion.objects.filter(emergencia=id_emergencia)
    atencion    = atencion[0]
    aspectoAten = AspectoAtencion.objects.filter(atencion=atencion,aspecto__parteaspecto__partecuerpo__nombre=parte_cuerpo)
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
            anomalia         = Anomalia.objects.filter(aspectoatencion=aspAten)
            descripcion      = request.POST['A'+str(aspAten.aspecto.id)]
            if anomalia:
                anomalia.descripcion = descripcion 
                anomalia.save() 
            else:
                anomalia = Anomalia(descripcion=descripcion,aspectoatencion=aspAten)
                anomalia.save()
            aspAten.save()
        elif input1 == 'no':
            aspAten.revisado = '0'
            anomalia         = Anomalia.objects.filter(aspectoatencion=aspAten)
            if anomalia:
                anomalia.delete()
            aspAten.save()
        
    return HttpResponse()
# --- RGV

#----------------------------------------------------------Gestion de INDICACIONES
@login_required(login_url='/')
def emergencia_indicaciones_ini(request,id_emergencia):
    emer = get_object_or_404(Emergencia,id=id_emergencia)
    paci = Paciente.objects.filter(emergencia__id=id_emergencia)
    paci = paci[0]
    triage = Triage.objects.filter(emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    ingreso = datetime.now()
    indicaciones = Indicacion.objects.filter(asignar__emergencia = id_emergencia)
    info = {'emergencia':emer,'triage':triage,'indicaciones':indicaciones, 'ingreso':ingreso}
    return render_to_response('atencion_ind.html',info,context_instance=RequestContext(request))

#Agrega las indicaciones dependiendo de la categoria: 
@login_required(login_url='/')
def emergencia_indicaciones(request,id_emergencia,tipo_ind):
    emer = get_object_or_404(Emergencia,id=id_emergencia)
    paci = Paciente.objects.filter(emergencia__id=id_emergencia)
    paci = paci[0]
    triage = Triage.objects.filter(emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    ingreso = datetime.now()
    mensaje = ""
    ya = ""

    #------------------ Gestion de indicaciones con interfaz de tabla----------------------#
    if tipo_ind == 'listar':
        indicaciones = Asignar.objects.filter(emergencia = id_emergencia,status=0)
        # print "Indicacion tipo en listar: ",indicaciones[0].indicacion.tipo
        # ed = EspDieta.objects.filter()
        info = {'mensaje':mensaje, 'emergencia':emer,'triage':triage,'indicaciones':indicaciones}
        return render_to_response('atencion_ind_listar.html',info,context_instance=RequestContext(request))

    elif tipo_ind == 'medicamento':
        indicaciones = Asignar.objects.filter(emergencia = id_emergencia,indicacion__tipo=tipo_ind,status=0)
        info = {'emergencia':emer,'triage':triage,'indicaciones':indicaciones, 'tipo_ind':tipo_ind}
        return render_to_response('atencion_ind_medica.html',info,context_instance=RequestContext(request))

    elif tipo_ind == 'valora' or tipo_ind == 'otros' or tipo_ind == 'terapeutico':
        indicaciones = Asignar.objects.filter(emergencia = id_emergencia,indicacion__tipo=tipo_ind,status=0)
        info = {'emergencia':emer,'triage':triage,'indicaciones':indicaciones, 'tipo_ind':tipo_ind}
        return render_to_response('atencion_ind_tera.html',info,context_instance=RequestContext(request))
    
    #------------ Gestion de indicaciones con interfaz de forms de Django-------------------#
    else:
        indicaciones = Asignar.objects.filter(emergencia = id_emergencia,status=0)
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
                print "IMprime lo que me retorna el form %s: "% (tipo_ind),nombre
                
                # Condicional para validar/agregar indicaciones de tipo lab/endoscopicos:
                if tipo_ind == 'lab' or tipo_ind == 'endoscopico':
                    for i in range(len(nombre)):
                        indicacionesQ = Indicacion.objects.filter(asignar__emergencia = id_emergencia,asignar__indicacion__nombre = nombre[i])
                        
                        if indicacionesQ:
                            mensaje = "Hay indicaciones con este nombre: "+ indicacionesQ[0].nombre
                            info = {'form':form,'mensaje':mensaje,'emergencia':emer,'tipo_ind':tipo_ind}
                            return render_to_response('atencion_ind_hidrata.html',info,context_instance=RequestContext(request))
                        
                        else:
                            indicaciones = Asignar.objects.filter(emergencia = id_emergencia,status=0)
                            # indicaciones = Asignar.objects.filter(emergencia = id_emergencia)
                            i= Indicacion.objects.get(nombre = nombre[i])
                            a = Asignar(emergencia=emer,indicacion=i,persona=emer.responsable,fecha=datetime.now(),fechaReal=datetime.now(),status=0)
                            a.save()

                    mensaje = "Procedimientos Guardados Exitosamente"
                    info = {'form':form,'mensaje':mensaje,'emergencia':emer,'triage':triage,'indicaciones':indicaciones,'tipo_ind':tipo_ind}
                    return render_to_response('atencion_ind_listar.html',info,context_instance=RequestContext(request))

                if tipo_ind == 'imagen':
                    for i in range(len(nombre)):
                        indicacionesQ = Indicacion.objects.filter(asignar__emergencia = id_emergencia,asignar__indicacion__nombre = nombre[i])
                        if indicacionesQ:
                            mensaje = "Hay indicaciones con este nombre: "+indicacionesQ[0].nombre
                            info = {'form':form,'mensaje':mensaje, 'tipo_ind':tipo_ind,'emergencia':emer}
                            return render_to_response('atencion_ind_hidrata.html',info,context_instance=RequestContext(request))
                        
                        else:
                            indicaciones = Asignar.objects.filter(emergencia = id_emergencia,status=0)
                            # indicaciones = Asignar.objects.filter(emergencia = id_emergencia)
                            i= Indicacion.objects.get(nombre = nombre[i])
                            a = Asignar(emergencia=emer,indicacion=i,persona=emer.responsable,fecha=datetime.now(),fechaReal=datetime.now(),status=0)
                            a.save()
                            p_cuerpo = request.POST["c_"+str(i.id)]
                            ex = EspImg(asignacion=a,parte_cuerpo=p_cuerpo)
                            ex.save()

                    mensaje = "Procedimientos Guardados Exitosamente"
                    info = {'form':form,'mensaje':mensaje,'emergencia':emer,'triage':triage,'indicaciones':indicaciones,'tipo_ind':tipo_ind}
                    return render_to_response('atencion_ind_listar.html',info,context_instance=RequestContext(request))

                # Condicional para validar/agregar indicaciones de tipo dieta e hidratacion
                else:
                    # indicacionesQ = Indicacion.objects.filter(asignar__emergencia = id_emergencia,asignar__indicacion__nombre = nombre)
                    indicacionesQ = Indicacion.objects.filter(asignar__emergencia = id_emergencia,asignar__indicacion__tipo = tipo_ind)
                    if indicacionesQ:
                        mensaje = "Hay indicaciones con este nombre: "+indicacionesQ[0].nombre
                        info = {'form':form,'mensaje':mensaje,'tipo_ind':tipo_ind,'emergencia':emer}
                        return render_to_response('atencion_ind_hidrata.html',info,context_instance=RequestContext(request))
                    else:
                        indicaciones = Asignar.objects.filter(emergencia = id_emergencia,status=0)
                        # indicaciones = Asignar.objects.filter(emergencia = id_emergencia)
                        i= Indicacion.objects.get(nombre = nombre)
                        a = Asignar(emergencia=emer,indicacion=i,persona=emer.responsable,fecha=datetime.now(),fechaReal=datetime.now(),status=0)
                        a.save()
                        if tipo_ind == 'dieta':
                            extra = pcd['observacion']
                            ex = EspDieta(asignacion=a,observacion=extra)
                            ex.save()
                        elif tipo_ind == 'hidrata':
                            sn = pcd['combina']
                            vol    = pcd['volumen']
                            vel    = pcd['vel_inf']
                            comp   = pcd['complementos']
                            ex = EspHidrata(asignacion=a,volumen=vol,vel_infusion=vel,complementos=comp)
                            ex.save()
                            if pcd['combina'] == "True":
                                ex_sol = pcd ['combina_sol']
                                i2= Indicacion.objects.get(nombre = ex_sol)
                                comb = CombinarHidrata(hidratacion1= ex,hidratacion2=i2)
                                comb.save()
                        mensaje = "Procedimientos Guardado Exitosamente"
                        info = {'form':form,'mensaje':mensaje,'emergencia':emer,'triage':triage,'indicaciones':indicaciones,'tipo_ind':tipo_ind}
                        return render_to_response('atencion_ind_listar.html',info,context_instance=RequestContext(request))

            else:
                form_errors = form.errors
                info = {'form':form,'mensaje':mensaje,'tipo_ind':tipo_ind,'form_errors': form_errors,'emergencia':emer}
                return render_to_response('atencion_ind_hidrata.html',info,context_instance=RequestContext(request))

        #---------Renderizado de formularios al ingresar por primera vez-----#
        if tipo_ind == 'dieta':
            d = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo = "dieta",status=0)
            
            if d:
                e = EspDieta.objects.filter(asignacion=d[0])
                print "ver observacion: ",e[0].observacion
                print "ver dietas iniciales", d
                print "Nombre Inicial: ", d[0].indicacion.nombre
                form = AgregarIndDietaForm(initial={'dieta':d[0].indicacion.pk,'observacion':e[0].observacion})
                mensaje = "Ya tiene agregadas las siguientes indicaciones"
                ya= "si"
                
            else:
                form = AgregarIndDietaForm()

        elif tipo_ind == 'hidrata':
            h = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo = "hidrata",status=0)
            if h:
                e = EspHidrata.objects.filter(asignacion=h[0])
                c = CombinarHidrata.objects.filter(hidratacion1 = e[0])
                mensaje = "Ya tiene agregadas las siguientes indicaciones"
                ya= "si"
                if c:
                    form = AgregarIndHidrataForm(initial={'hidrata':h[0].indicacion.pk,'combina':True,'combina_sol':c[0].hidratacion2.pk,'volumen':e[0].volumen,'vel_inf':e[0].vel_infusion,'complementos':e[0].complementos})
                else:
                    form = AgregarIndHidrataForm(initial={'hidrata':h[0].indicacion.pk,'combina':False,'volumen':e[0].volumen,'vel_inf':e[0].vel_infusion,'complementos':e[0].complementos})
            else:
                form = AgregarIndHidrataForm()

        elif tipo_ind == 'lab':
            labi = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo = "lab",status=0)
            if labi:
                lab_list=[]
                for l in labi:
                    lab_list.append(l.indicacion.pk)
                
                form = AgregarIndLabForm(initial={'lab':lab_list})
                mensaje = "Ya tiene agregadas las siguientes indicaciones"
                ya= "si"
            else:
                form = AgregarIndLabForm()

        elif tipo_ind == 'imagen':
            img = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo = "imagen",status=0)
            if img:
                img_list=[]
                for im in img:
                    img_list.append(im.indicacion.pk)
                
                form = AgregarIndImgForm(initial={'imagen':img_list})
                mensaje = "Ya tiene agregadas las siguientes indicaciones"
                ya= "si"
            else:
                form = AgregarIndImgForm()

        elif tipo_ind == 'endoscopico':
            end = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo = "endoscopico",status=0)
            if end:
                end_list=[]
                
                for e in end:
                    end_list.append(e.indicacion.pk)
                
                form = AgregarIndEndosForm(initial={'endoscopico':end_list})
                mensaje = "Ya tiene agregadas las siguientes indicaciones"
            else:
                form = AgregarIndEndosForm()
        
        info = {'form':form,'mensaje':mensaje,'tipo_ind':tipo_ind, 'ya':ya,'emergencia':emer}
        return render_to_response('atencion_ind_hidrata.html',info,context_instance=RequestContext(request))

#--------------------------------------------Listar Info Extra
@login_required(login_url='/')
def emergencia_indicacion_info(request,id_asignacion,tipo_ind):
    extra2=""
    extra=""
    if tipo_ind=="dieta":
        extra= EspDieta.objects.get(asignacion=id_asignacion)

    elif tipo_ind=="hidrata":
        extra = EspHidrata.objects.get(asignacion=id_asignacion)
        ver = CombinarHidrata.objects.filter(hidratacion1=extra)
        if ver:
            extra2=ver[0]

    elif tipo_ind=="medicamento":
        extra = EspMedics.objects.get(asignacion=id_asignacion)
        ver = tieneSOS.objects.filter(espMed=extra)
        if ver:
            extra2=ver[0]

    elif tipo_ind=="imagen":
        extra = EspImg.objects.get(asignacion=id_asignacion)
        
    info = {'tipo_ind':tipo_ind, 'extra':extra, 'extra2':extra2}
    return render_to_response('atencion_ind_listExtra.html',info,context_instance=RequestContext(request))

#-----------------------------------------------Acciones CRUD
#--------------------------------------------AGREGAR
@login_required(login_url='/')
def emergencia_indicaciones_agregar(request,id_emergencia,tipo_ind):
    emer = get_object_or_404(Emergencia,id=id_emergencia)
    paci = Paciente.objects.filter(emergencia__id=id_emergencia)
    paci = paci[0]
    triage = Triage.objects.filter(emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    mensaje = ""
    atencion = Atencion.objects.filter(emergencia= emer)
    diags = EstablecerDiag.objects.filter(atencion=atencion[0])
    
    if request.method == 'POST':
        if tipo_ind == 'diagnostico':
            diagnostico  = request.POST.getlist('nuevoDiag')
            #Consulta diagnosticos:
            ver = range(len(diagnostico)-1)
            for i in ver:
                # Condicional para saber si existen los diagnosticos:
                diagnosticoQ = Diagnostico.objects.filter(establecerdiag__atencion = atencion[0],establecerdiag__diagnostico__nombreD = diagnostico[i])
                if diagnosticoQ:
                    mensaje = "Hay Diagnosticos con este nombre: "+diagnosticoQ[0].nombreD
                    info = {'mensaje':mensaje,'emergencia':emer,'triage':triage,'tipo_ind':tipo_ind,'diags':diags}
                    return render_to_response('atencion_diag.html',info,context_instance=RequestContext(request))
                else:
                    diag = Diagnostico(nombreD=diagnostico[i])
                    diag.save()
                    est_Diag = EstablecerDiag(atencion=atencion[0],diagnostico=diag,fecha=datetime.now(),fechaReal=datetime.now())
                    est_Diag.save()
            mensaje = "Diagnosticos guardados Exitosamente"
            info = {'mensaje':mensaje,'emergencia':emer,'triage':triage,'tipo_ind':tipo_ind,'diags':diags}
            return render_to_response('atencion_diag.html',info,context_instance=RequestContext(request))

        elif tipo_ind == 'valora' or tipo_ind == 'otros' or tipo_ind == 'terapeutico':
            indicaciones = Asignar.objects.filter(emergencia = id_emergencia,indicacion__tipo=tipo_ind)
            nombres         = request.POST.getlist('nuevaInd')
            ver = range(len(nombres)-1)
            for i in ver:
                # Condicional para saber si existe en las indicaciones:
                indicacionesQ = Indicacion.objects.filter(asignar__emergencia = id_emergencia,asignar__indicacion__nombre = nombres[i])
                if indicacionesQ:
                    mensaje = "Hay indicaciones con este nombre: "+indicacionesQ[0].nombre
                    info = {'mensaje':mensaje,'emergencia':emer,'triage':triage,'indicaciones':indicaciones,'tipo_ind':tipo_ind}
                    return render_to_response('atencion_ind_tera.html',info,context_instance=RequestContext(request))
                else:
                    #Creo el objeto indicacion
                    ind = Indicacion(nombre=nombres[i],tipo=tipo_ind)
                    ind.save()
                    a = Asignar(emergencia=emer,indicacion=ind,persona=emer.responsable,fecha=datetime.now(),fechaReal=datetime.now(),status=0)
                    a.save()
            mensaje = "Indicaciones guardadas Exitosamente"
            info = {'mensaje':mensaje,'emergencia':emer,'triage':triage,'indicaciones':indicaciones,'tipo_ind':tipo_ind}
            return render_to_response('atencion_ind_tera.html',info,context_instance=RequestContext(request))

        elif tipo_ind == 'medicamento':
            indicaciones = Asignar.objects.filter(emergencia = id_emergencia,indicacion__tipo=tipo_ind)
            nombres         = request.POST.getlist('nuevaMed')
            dosis           = request.POST.getlist('nuevaDosis')
            tc              = request.POST.getlist('nuevoTC')
            frec            = request.POST.getlist('nuevaFrec')
            via             = request.POST.getlist('nuevaVAD')
            tf              = request.POST.getlist('nuevoTF')
            situacion       = request.POST.getlist('situacion')
            comentario      = request.POST.getlist('comentario')
            ver = range(len(nombres)-1)
            print "nombres", nombres
            print "Situacion", situacion
            print "Comentarios", comentario

            print "verr rango: "+str(ver)
            
            for i in ver:
                # Condicional para saber si existe en las indicaciones:
                indicacionesQ = Indicacion.objects.filter(asignar__emergencia = id_emergencia,asignar__indicacion__nombre = nombres[i])
                if indicacionesQ:
                    mensaje = "Hay indicaciones con este nombre: "+indicacionesQ[0].nombre
                    info = {'mensaje':mensaje,'emergencia':emer,'triage':triage,'indicaciones':indicaciones,'tipo_ind':tipo_ind}
                    return render_to_response('atencion_ind_medica.html',info,context_instance=RequestContext(request))
                else:
                    #Creo el objeto indicacion
                    print "nombre: ",nombres[i]
                    ind = Indicacion(nombre=nombres[i],tipo=tipo_ind)
                    ind.save()
                    a = Asignar(emergencia=emer,indicacion=ind,persona=emer.responsable,fecha=datetime.now(),fechaReal=datetime.now(),status=0)
                    a.save()
                    # Agregar info extra:
                    eMed= EspMedics(asignacion=a,dosis=float(dosis[i]),tipo_conc =tc[i],frecuencia=frec[i],tipo_frec=tf[i],via_admin=via[i])
                    eMed.save()
                    print "Objeto guardado numero: "+str(i)+"\n"
                    print eMed.asignacion.indicacion.nombre
                    if tf[i] =="sos":
                        print "situaciones = ", situacion
                        print "comentarios = ", comentario
                        print "situaciones numero: "+str(i)+"\n"
                        print situacion[i]
                        print "comentarios numero: "+str(i)+"\n"
                        print comentario[i]
                        tSos= tieneSOS(espMed=eMed,situacion=situacion[i],comentario=comentario[i])
                        tSos.save()
                    
            mensaje = "Medicaciones guardadas Exitosamente"
            info = {'mensaje':mensaje,'emergencia':emer,'triage':triage,'indicaciones':indicaciones,'tipo_ind':tipo_ind}
            return render_to_response('atencion_ind_medica.html',info,context_instance=RequestContext(request))
    else:
        mensaje = "ELSE PORQ NO HAY POST"
        info = {'mensaje':mensaje,'emergencia':emer,'triage':triage,'indicaciones':indicaciones,'tipo_ind':tipo_ind}
        return render_to_response('atencion_ind_medica.html',info,context_instance=RequestContext(request))


#--------------------------------------------ELIMINAR
@login_required(login_url='/')
def emergencia_indicaciones_eliminar(request,id_emergencia,tipo_ind):
    emer = get_object_or_404(Emergencia,id=id_emergencia)
    paci = Paciente.objects.filter(emergencia__id=id_emergencia)
    paci = paci[0]
    triage = Triage.objects.filter(emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    mensaje = ""
    atencion = Atencion.objects.filter(emergencia= emer)
    
    if request.method == 'POST':
        checkes = request.POST.getlist(u'check')
        
        if tipo_ind == "diagnostico":
            # obj tiene el id de la relacion
            for obj in checkes:
                relDiag = EstablecerDiag.objects.get(id=obj)
                # Borro ese objeto:
                relDiag.delete()
                diags = EstablecerDiag.objects.filter(atencion=atencion[0])
            mensaje = "Diagnosticos eliminado Exitosamente"
            info = {'mensaje':mensaje,'emergencia':emer,'triage':triage,'tipo_ind':tipo_ind,'diags':diags}
            return render_to_response('atencion_diag.html',info,context_instance=RequestContext(request))
        
        elif tipo_ind == "normal":
            for obj in checkes:
                asig = Asignar.objects.get(id=obj)
                tipo = asig.indicacion.tipo
                print "ASIG object: ",asig

                asig.status=1
                asig.save()

            indicaciones = Asignar.objects.filter(emergencia = id_emergencia,status=0)
            mensaje = "Cambio de status realizado Exitosamente"
            info = {'mensaje':mensaje, 'emergencia':emer,'triage':triage,'indicaciones':indicaciones, 'tipo_ind':tipo_ind}
            return render_to_response('atencion_ind_listar.html',info,context_instance=RequestContext(request))

#--------------------------------------------MODIFICAR
def emergencia_indicaciones_modificar(request,id_emergencia,tipo_ind):
    emer   = get_object_or_404(Emergencia,id=id_emergencia)
    paci = Paciente.objects.filter(emergencia__id=id_emergencia)
    paci = paci[0]
    triage = Triage.objects.filter(emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    mensaje = ""

    if tipo_ind =="diagnostico":
        at = Atencion.objects.filter(emergencia=id_emergencia)
        diags = EstablecerDiag.objects.filter(atencion=at[0])
        for da in diags:
            # No verifica si nombre ya existe:
            da.diagnostico.nombreD = request.POST[str(da.id)+"nombre"]
            d= Diagnostico.objects.get(id = da.diagnostico.id)
            d.nombreD = request.POST[str(da.id)+"nombre"]
            d.save()
            da.save()
            
        diagsN = EstablecerDiag.objects.filter(atencion=at[0])
        mensaje = " Modificado Exitosamente "
        info = {'mensaje':mensaje, 'emergencia':emer,'diags':diagsN, 'tipo_ind':tipo_ind}
        return render_to_response('atencion_diag.html',info,context_instance=RequestContext(request))

    elif tipo_ind == 'valora' or tipo_ind == 'otros' or tipo_ind == 'terapeutico':
        indicaciones = Asignar.objects.filter(emergencia = id_emergencia,indicacion__tipo=tipo_ind)
        for ia in indicaciones:
            # No verifica si nombre ya existe:
            ia.indicacion.nombre = request.POST[str(ia.id)+"nombre"]
            i= Indicacion.objects.get(id = ia.indicacion.id)
            i.nombre = request.POST[str(ia.id)+"nombre"]
            i.save()
            ia.save()
        indsN = Asignar.objects.filter(emergencia = id_emergencia,indicacion__tipo=tipo_ind)
        mensaje = " Modificado Exitosamente "
        info = {'mensaje':mensaje, 'emergencia':emer,'indicaciones':indsN, 'tipo_ind':tipo_ind}
        return render_to_response('atencion_ind_tera.html',info,context_instance=RequestContext(request))
    
    elif tipo_ind =="medicamento":
        indicaciones = Asignar.objects.filter(emergencia = id_emergencia,indicacion__tipo=tipo_ind)
        for ind in indicaciones:
            ind.indicacion.nombre = request.POST[str(ind.id)+"nombre"]
            ii= Indicacion.objects.get(id = ind.indicacion.id)
            ii.nombre = request.POST[str(ind.id)+"nombre"]
            ii.save()
            ind.save()
            extraO = EspMedics.objects.get(asignacion = ind)
            extraO.dosis=request.POST[str(ind.id)+"dosis"]
            extraO.tipo_conc=request.POST[str(ind.id)+"conc"]
            extraO.frecuencia = request.POST[str(ind.id)+"frec"]
            # Falta agregar los inputs para modificar comentario y situacion:
            # extraO.tipo_frec = request.POST[str(ind.id)+"t_frec"]
            extraO.via_admin = request.POST[str(ind.id)+"via_adm"]
            extraO.save()
            
        indicaciones = Asignar.objects.filter(emergencia = id_emergencia,indicacion__tipo=tipo_ind)
        print "Pastillas asignadas",indicaciones
        mensaje = " Modificado Exitosamente"
        info = {'mensaje':mensaje, 'emergencia':emer,'triage':triage,'indicaciones':indicaciones, 'tipo_ind':tipo_ind}
        return render_to_response('atencion_ind_medica.html',info,context_instance=RequestContext(request))

#----------------------------------Gestion de Diagnostico Definitivo
@login_required(login_url='/')
def emergencia_diagnostico(request,id_emergencia):
    emer = get_object_or_404(Emergencia,id=id_emergencia)
    paci = Paciente.objects.filter(emergencia__id=id_emergencia)
    paci = paci[0]
    triage = Triage.objects.filter(emergencia=id_emergencia).order_by("-fechaReal")
    triage = triage[0]
    tipo_ind = 'diagnostico'
    at = Atencion.objects.filter(emergencia=id_emergencia)
    diags = EstablecerDiag.objects.filter(atencion=at[0])
    mensaje = ""
    info = {'mensaje':mensaje, 'emergencia':emer,'triage':triage,'diags':diags,'tipo_ind':tipo_ind}
    return render_to_response('atencion_diag.html',info,context_instance=RequestContext(request))

# Funcion que recibe el formulario para evaluar a un paciente y lo procesa
@login_required(login_url='/')
def evaluar_paciente(request, id_emergencia):
  if request.method == 'POST':
    form = FormularioEvaluacionPaciente(request.POST)
    es_valido = form.is_valid()

    if es_valido:
      emergencia = get_object_or_404(Emergencia, id = id_emergencia)
      medico = Usuario.objects.get(username = request.user)
      evaluacion = form.cleaned_data
      paciente = emergencia.paciente
      paciente.signos_tmp = evaluacion['temperatura']
      paciente.signos_fc = evaluacion['frecuencia_cardiaca']
      paciente.signos_fr = evaluacion['frecuencia_respiratoria']
      paciente.signos_pa = evaluacion['presion_diastolica']
      paciente.signos_pb = evaluacion['presion_sistolica']
      paciente.signos_saod = evaluacion['saturacion_oxigeno']

      paciente.save()

    csrf_token_value = request.COOKIES['csrftoken']
    plantilla_formulario = render_to_string(
                             'formularios/evaluacionPaciente.html',
                             { 'idE': id_emergencia, 
                               'csrf_token_value': csrf_token_value,
                               'form': form })
    return render(request,
                  'scripts/evaluacionPaciente.js',
                  { 'es_valido': es_valido,
                    'id_emergencia': id_emergencia,
                    'plantilla_formulario': plantilla_formulario },
                  content_type = 'text/javascript')

def agregarEnfermedad(request,nombre_enfermedad):
  string = nombre_enfermedad
  Sugerencias= serializers.serialize("json",Enfermedad.objects.filter(descripcion__icontains = string)[:5])
  return HttpResponse(json.dumps(Sugerencias),
                        content_type='application/json')
