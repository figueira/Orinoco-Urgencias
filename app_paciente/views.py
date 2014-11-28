# Manejo de Sesion
from django.contrib.auth.decorators import login_required

# Formularios
from django.core.context_processors import csrf
from django.template import RequestContext

# General HTML
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

# JSON
from django.core import serializers
import json

# Manejo de Informacion de esta aplicacion
from forms import *
from models import *
from app_perfil.views import paciente_perfil
from app_emergencia.models import Emergencia

# Manejo de exepciones
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.


@login_required(login_url='/')
def paciente_agregar(request):
    mensaje = ""
    if request.method == 'POST':
        form = AgregarPacienteForm(request.POST)
        if form.is_valid():
            pcd = form.cleaned_data
            p_cedula = pcd['cedula']
            p_nombres = pcd['nombres']
            p_apellidos = pcd['apellidos']
            p_sexo = pcd['sexo']
            p_fecha_nacimiento = pcd['fecha_nacimiento']
            p_cel = pcd['cod_cel'] + pcd['num_cel']
            p_email = pcd['email']
            p_direccion = pcd['direccion']
            p_tlf_casa = pcd['cod_tlf_casa'] + pcd['num_tlf_casa']
            p_contacto_nombre = pcd['contacto_nombre']
            p_contacto_tlf = pcd['contacto_cod_tlf'] + pcd['contacto_num_tlf']
            prueba = Paciente.objects.filter(cedula=p_cedula)
            if not prueba:
                p = Paciente(
                    cedula=p_cedula,
                    nombres=p_nombres,
                    apellidos=p_apellidos,
                    sexo=p_sexo,
                    fecha_nacimiento=p_fecha_nacimiento,
                    tlf_cel=p_cel,
                    email=p_email,
                    direccion=p_direccion,
                    tlf_casa=p_tlf_casa,
                    contacto_nom=p_contacto_nombre,
                    contacto_tlf=p_contacto_tlf
                )
                p.save()
                return redirect('/')
            else:
                mensaje = "Ya hay un paciente registrado con esa cedula"
        info = {
            'form': form,
            'mensaje': mensaje
        }
        return render_to_response(
            'agregarPaciente.html',
            info,
            context_instance=RequestContext(request))
    form = AgregarPacienteForm()
    info = {
        'form': form
    }
    return render_to_response(
        'agregarPaciente.html',
        info,
        context_instance=RequestContext(request))


@login_required(login_url='/')
def paciente_listarPacientes(request):
    listaP = Paciente.objects.all()
    info = {
        'listaP': listaP
    }
    return render_to_response(
        'listaGeneral.html',
        info,
        context_instance=RequestContext(request))


@login_required(login_url='/')
def buscarPacienteJson(request, ced):
    pacientes = serializers.serialize(
        "json",
        Paciente.objects.filter(cedula__startswith=ced))
    response_data = {
        'result': 'success',
        'message': pacientes,
    }
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


@login_required(login_url='/')
def buscarEnfermedad(request, nombre_enfermedad):
    string = nombre_enfermedad
    Sugerencias = serializers.serialize(
        "json",
        Enfermedad.objects.filter(descripcion__icontains=string)[:10])
    return HttpResponse(
        json.dumps(Sugerencias),
        content_type='application/json')


@login_required(login_url='/')
def agregarEnfermedad(request, codigo_enfermedad, codigo_paciente):
    try:
        enfermedad = Enfermedad.objects.get(id=codigo_enfermedad)
        paciente = Paciente.objects.get(id=codigo_paciente)
        paciente.enfermedades.add(enfermedad)
        success = {
            'message': "Enfermead agregada exitosamente",
            'result': 1
        }
        return HttpResponse(json.dumps(success), mimetype="application/json")

    except ObjectDoesNotExist:
        fail = {
            'message': u'Agregacion fallida. Esta enfermedad no se encuentra en la base de datos'.encode('utf-8'),
            'resutl': 0
        }
        return HttpResponse(json.dumps(fail), mimetype="application/json")


@login_required(login_url='/')
def editarPaciente(request, idP):
    paciente = get_object_or_404(Paciente, pk=idP)
    if request.method == 'POST':
        form = EditarPacienteForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            cedulas = data['cedula']
            nombre = data['nombres']
            apellido = data['apellidos']
            correo = data['email']
            fecha_nacimiento = data['fecha_nacimiento']

            paciente.cedula = cedulas
            paciente.nombres = nombre
            paciente.apellidos = apellido
            paciente.email = correo
            paciente.fecha_nacimiento = fecha_nacimiento

            paciente.save()
        else:
            info = {
                'form': form,
                'paciente': paciente}
            return render_to_response(
                'editarPerfil.html',
                info,
                context_instance=RequestContext(request))
    else:
        form = EditarPacienteForm(initial={
            'cedula': paciente.cedula,
            'nombres': paciente.nombres,
            'apellidos': paciente.apellidos,
            'email': paciente.email,
            'fecha_nacimiento': paciente.fecha()
            })
        info = {
            'form': form,
            'paciente': paciente
        }
        return render_to_response(
            'editarPerfil.html',
            info,
            context_instance=RequestContext(request))
    return paciente_perfil(request, idP)


@login_required(login_url='/')
def eliminarEnfermedad(request, codigo_enfermedad, codigo_paciente):
    paciente = Paciente.objects.get(id=codigo_paciente)
    enfermedad = Enfermedad.objects.get(id=codigo_enfermedad)
    paciente.enfermedades.remove(enfermedad)
    success = {
        'result': 1
    }
    return HttpResponse(json.dumps(success), mimetype="application/json")


@login_required(login_url='/')
def ver_emergencias(request, idP):
    e = Emergencia.objects.filter(paciente=idP).order_by('-hora_ingreso')
    print e
    info = {
        'lista': e
    }
    return render_to_response(
        'emergencias.html',
        info,
        context_instance=RequestContext(request))
