# -*- encoding: utf-8 -*-
from django.contrib.auth.decorators import login_required

# Formularios
from django.core.context_processors import csrf
from django.template import RequestContext

# General HTML
from django.shortcuts import render_to_response,redirect,get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

# Manejo de Informacion de esta aplicacion
from datetime import datetime
from app_emergencia.forms import *

# PDF
import cStringIO as StringIO
from app_emergencia.pdf import *
import cgi
from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import HttpResponse


# Create your views here.
@login_required(login_url='/')
def paciente_perfil(request, idP):
    paciente = get_object_or_404(Paciente, pk=idP)
    es = Emergencia.objects.filter(paciente=paciente).order_by('hora_egreso')
    # tam = len(es)
    ea = es.last()
    # ea = ea[0]
    t = Triage.objects.filter(emergencia=ea).last()
    # if t is not None:
    #     t = t[0]
    # else:
    #     t = None
    info = {
        'p': paciente,
        'ea': ea,
        't': t
    }
    return render_to_response(
        'app_perfil/perfil.html',
        info,
        context_instance=RequestContext(request)
    )


@login_required(login_url='/')
def reporte_triage(request, idP):
    return reporte_triage_pdf(request, idP)
