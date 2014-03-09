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
import ho.pisa as pisa
import cStringIO as StringIO
import cgi
from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import HttpResponse


# Create your views here.
@login_required(login_url='/')
def paciente_perfil(request,idP):
    p = get_object_or_404(Paciente,pk=idP)
    es = Emergencia.objects.filter(paciente=p) \
                                  .order_by('hora_egreso')
    tam = len(es)
    ea = es[tam-1]
    # ea = ea[0]
    info = {'p':p,'ea':ea,'es':es}
    return render_to_response('perfil.html',info,context_instance=RequestContext(request))

@login_required(login_url='/')
def reporte_triage(request,idP):
    p = get_object_or_404(Paciente,pk=idP)
    ea = Emergencia.objects.filter(paciente=p)
    ea = ea[0]
    es = Emergencia.objects.filter(paciente=p)
    info = {'p':p,'ea':ea,'es':es}
    html = render_to_string('reporteTriage.html',info, context_instance=RequestContext(request))
    response = HttpResponse(content_type='application/pdf')
    return generar_pdf(html)

def generar_pdf(html):
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), result, encoding='UTF-8')
    if not pdf.err:
        return HttpResponse(result.getvalue(), mimetype='application/pdf')
    return HttpResponse('Error al generar el PDF: %s' % cgi.escape(html))

def get_full_path_x(request):
    full_path = ('http', ('', 's')[request.is_secure()], '://',
    request.META['HTTP_HOST'], request.path)
    return ''.join(full_path) 
