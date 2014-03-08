# -*- encoding: utf-8 -*-
# Manejo de Sesion
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Formularios
from django.core.context_processors import csrf
from django.template import RequestContext
from django.forms.widgets import CheckboxSelectMultiple

# General HTML
from django.shortcuts import render_to_response,redirect,get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

# Manejo de Informacion de esta aplicacion
from forms import *
from models import *

# Envio de Correos
from django.core.mail import EmailMessage

# Create your views here.
def sesion_iniciar(request):
    if request.user.is_authenticated():
        info = {}
        return render_to_response('loged.html',info,context_instance=RequestContext(request))
    if request.method == 'POST':
        unombre = request.POST.get('unombre', 'userDefault')
        uclave  = request.POST.get('uclave', 'psswdDefault')
        user = authenticate(username=unombre,password=uclave)
        
        #Si le doy a iniciar sesion y NO estoy en el home, tengo userDefault y
        #psswdDefault, redirecciono al home para introducir datos
        if unombre == "userDefault" and uclave=="psswdDefault":
            msj_tipo = ""
            msj_info = ""
            form = IniciarSesionForm()
            info = {'msj_tipo':msj_tipo,'msj_info':msj_info,'form':form}
            return render_to_response('index.html',info,context_instance=RequestContext(request))

        if user is not None:
            if user.is_active:
                login(request,user)
                info = {}
                return render_to_response('loged.html',info,context_instance=RequestContext(request))

        msj_tipo = "error"
        msj_info = "Error en clave"
        form = IniciarSesionForm()
        info = {'msj_tipo':msj_tipo,'msj_info':msj_info,'form':form}
        return render_to_response('index.html',info,context_instance=RequestContext(request))
    form = IniciarSesionForm()
    info = {'form':form}
    return render_to_response('index.html',info,context_instance=RequestContext(request))

def sesion_cerrar(request):
    logout(request)
    return redirect('/')

def usuario_solicitar(request):
    mensaje = ""
    if request.method == 'POST':
        form = SolicitarCuenta(request.POST)
        if form.is_valid():
            pcd = form.cleaned_data
            u_cedula           = pcd['cedula']
            u_nombres          = pcd['nombres']
            u_apellidos        = pcd['apellidos']
            u_tipo		         = pcd['tipo']
            u_sexo             = pcd['sexo']
            u_cel              = pcd['cod_cel'] + pcd['num_cel']
            u_direccion        = pcd['direccion']
            u_tlf_casa         = pcd['cod_casa'] + pcd['num_casa']
            u_email            = pcd['email']
            u_clave            = pcd['clave']
            u_clave0           = pcd['clave0']
            u_administrador    = pcd['administrador']
            prueba = Usuario.objects.filter(cedula=u_cedula)
            prueba2 = (u_clave==u_clave0)
            if not prueba:
                if prueba2:
		              u = Usuario(username=u_cedula,cedula=u_cedula,first_name=u_nombres,habilitado=False,last_name=u_apellidos,tipo=u_tipo,administrador=u_administrador,sexo=u_sexo,tlf_cel=u_cel,direccion=u_direccion,tlf_casa=u_tlf_casa,email=u_email,password=u_clave)
		              u.is_active = True
		              u.set_password(u_clave)
		              if u_administrador == True:
		                  u.is_staff = True
		              u.save() 	
		              return redirect('/')
                else:
		                msj_info = "No hubo coincidencia con las claves ingresadas"     
            else:
		            msj_info = "Ya hay un usuario registrado con esa cedula"     
        else:
            msj_info = "Error con el formulario"
        msj_tipo = "error"
        info = {'msj_tipo':msj_tipo,'msj_info':msj_info,'form':form}
        return render_to_response('solicitar.html',info,context_instance=RequestContext(request))
    form = SolicitarCuenta()
    info = {'form':form}
    return render_to_response('solicitar.html',info,context_instance=RequestContext(request))

@login_required(login_url='/')
def usario_listarPendientes(request):    
    listaP = Usuario.objects.filter(habilitado=False)
    info = {'listaP':listaP} 
    return render_to_response('usuariosPendientes.html',info,context_instance=RequestContext(request))

@login_required(login_url='/')
def usario_listarRechazados(request):    
    listaP = Usuario.objects.filter(habilitado=False)
    info = {'listaP':listaP}
    return render_to_response('usuariosPendientes.html',info,context_instance=RequestContext(request))

@login_required(login_url='/')
def usario_listar(request):    
    listaU = Usuario.objects.filter(habilitado=True)
    info = {'listaU':listaU}
    return render_to_response('listaUsuarios.html',info,context_instance=RequestContext(request))

@login_required(login_url='/')
def usuario_rechazar(request,cedulaU):
    usuario = get_object_or_404(Usuario,cedula=cedulaU)
    usuario.delete()
    return redirect("/usuario/pendientes")

@login_required(login_url='/')
def usuario_aprobar(request,cedulaU):
	usuario = get_object_or_404(Usuario,cedula=cedulaU)
	usuario.habilitado = True
	usuario.is_active = True
	usuario.save()
	email = EmailMessage('[GenSE] Admin - Activacion de Cuenta','Estimado/a '+usuario.first_name+' '+usuario.last_name+'\n\nSe aprobo su solicitud de activacion de cuenta\n\nSaludos,\nAdministrador del Sistema', to=[usuario.email]) 
	email.send()
	return redirect("/usuario/pendientes")

@login_required(login_url='/')
def pendiente_examinar(request,cedulaU):
    usuario = get_object_or_404(Usuario,cedula=cedulaU)
    info = {'usuario':usuario}
    return render_to_response('pendienteExaminar.html',info,context_instance=RequestContext(request))

@login_required(login_url='/')
def clave_cambiar(request):
    mensaje = ""
    if request.method == 'POST':
        form = cambioClave(request.POST)
        if form.is_valid():
            pcd = form.cleaned_data
            f_claveV          = pcd['claveV']
            f_clave           = pcd['clave']
            f_claveO          = pcd['claveO']
            usuario           = Usuario.objects.get(username=request.user)
            if usuario.check_password(f_claveV):
                if (f_clave == f_claveO):
                    usuario.set_password(f_clave)
                    usuario.save()
                    mensaje = "Clave cambiada"
                    form = cambioClave()
                    info = {'form':form,'mensaje':mensaje}
                    return render_to_response('cambiarClave.html',info,context_instance=RequestContext(request))                    
                else:
                    mensaje = "Las dos claves son distintas"
            else:
                mensaje = "La clave vieja no es correcta"
        else:
            mensaje = "Error con el formulario"
        info = {'form':form,'mensaje':mensaje}
        return render_to_response('cambiarClave.html',info,context_instance=RequestContext(request))
    form = cambioClave()
    info = {'form':form,'mensaje':mensaje}
    return render_to_response('cambiarClave.html',info,context_instance=RequestContext(request))

def clave_restablecer(request):
    mensaje = ""
    if request.method == 'POST':
        form = restablecerClave(request.POST)
        if form.is_valid():
            pcd = form.cleaned_data
            f_correo = pcd['correo']
            usuario = Usuario.objects.filter(email=f_correo)
            if len(usuario) == 0 :
                mensaje = "Correo Invalido"
            else:
                usuario = usuario[0]
                clave = User.objects.make_random_password()
                email = EmailMessage('[GenSE] Admin - Cambio de Clave','Estimado/a '+usuario.first_name+' '+usuario.last_name+'\n\nSe recibio una solicitud de cambiar su clave, la nueva clave es: '+clave+'\n\nSaludos,\nAdministrador del Sistema', to=[f_correo]) 
                email.send()
                usuario.set_password(clave)
                usuario.save()
                mensaje = "Su nueva clave fue enviada al correo suministrado"
                form = restablecerClave()
                info = {'form':form,'mensaje':mensaje}
                return render_to_response('restablecerClave.html',info,context_instance=RequestContext(request))
        else:
            mensaje = "Error con el formulario"
    form = restablecerClave()
    info = {'form':form,'mensaje':mensaje}
    return render_to_response('restablecerClave.html',info,context_instance=RequestContext(request))

def usuario_crear(request):
    mensaje = ""
    if request.method == 'POST':
        form = SolicitarCuenta(request.POST)
        if form.is_valid():
            pcd = form.cleaned_data
            u_cedula           = pcd['cedula']
            u_nombres          = pcd['nombres']
            u_apellidos        = pcd['apellidos']
            u_tipo		         = pcd['tipo']
            u_sexo             = pcd['sexo']
            u_cel              = pcd['cod_cel'] + pcd['num_cel']
            u_direccion        = pcd['direccion']
            u_tlf_casa         = pcd['cod_casa'] + pcd['num_casa']
            u_email            = pcd['email']
            u_clave            = pcd['clave']
            u_clave0           = pcd['clave0']
            u_administrador    = pcd['administrador']
            prueba = Usuario.objects.filter(cedula=u_cedula)
            prueba2 = (u_clave==u_clave0)
            if not prueba:
                if prueba2:
		              u = Usuario(username=u_cedula,cedula=u_cedula,first_name=u_nombres,habilitado=True,last_name=u_apellidos,tipo=u_tipo,administrador=u_administrador,sexo=u_sexo,tlf_cel=u_cel,direccion=u_direccion,tlf_casa=u_tlf_casa,email=u_email,password=u_clave)
		              u.is_active = True
		              u.set_password(u_clave)
		              if u_administrador == True:
		                  u.is_staff = True
		              u.save() 	
		              return redirect('/')
                else:
		            	msj_info = "No hubo coincidencia con las claves ingresadas"     
            else:
		        	msj_info = "Ya hay un usuario registrado con esa cedula"     
        else:
        	msj_info = "Error con el formulario"
        msj_tipo = "error"
        info = {'msj_tipo':msj_tipo,'msj_info':msj_info,'form':form}
        return render_to_response('crearUsuario.html',info,context_instance=RequestContext(request))
    form = SolicitarCuenta()
    info = {'form':form}
    return render_to_response('crearUsuario.html',info,context_instance=RequestContext(request))

@login_required(login_url='/')
def usuario_deshabilitar(request,cedulaU):
    usuario = get_object_or_404(Usuario,cedula=cedulaU)
    usuario.is_active = False
    usuario.save()
    return redirect("/usuario/listar")

@login_required(login_url='/')
def usuario_habilitar(request,cedulaU):
	usuario = get_object_or_404(Usuario,cedula=cedulaU)
	usuario.is_active = True
	usuario.save()
	return redirect("/usuario/listar")

@login_required(login_url='/')
def usuario_examinar(request,cedulaU):
    usuario = get_object_or_404(Usuario,cedula=cedulaU)
    info = {'usuario':usuario}
    return render_to_response('usuarioExaminar.html',info)
