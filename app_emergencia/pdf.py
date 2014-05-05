  # -*- encoding: utf-8 -*-
# coding: latin1

# General HTML
from django.shortcuts import render_to_response, redirect, get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect

# Manejo de Informacion de esta aplicacion
from django.utils.timezone import utc
from datetime import datetime, date, timedelta
from models import *
from forms import *
from app_usuario.forms import *


#####################################################
#Imports Atencion
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from reportlab.platypus.flowables import *
from reportlab.lib.colors import pink, black, red, lightblue, white

from app_enfermedad.models import *
from app_paciente.models import *
######################################################

def header_pdf(c,h1,h2):
  # move the origin up and to the left
  c.translate(inch,inch)
  # define a large font
  c.drawInlineImage("static/img/logoazul.png", -50,700, width=40, height=60)
  c.setFont("Helvetica", 8)
  c.drawString(10, 740,"Centro Medico de Caracas")
  c.drawString(10, 730, "Av. Eraso, Plaza El Estanque")
  c.drawString(10, 720, "Urb. San Bernardino, Caracas, Venezuela")
  c.drawString(10, 710, "Tel. 58+ 212-555-9111 / 555-9486 / 552-2222")

  c.setFont("Helvetica", 22)
  # choose some colors
  c.setStrokeColor(lightblue)                  #borde del rectangulo
  c.setFillColor(lightblue)                         #color de fondo
  # draw a rectangle
  c.rect(-inch,8.4*inch,3.7*inch,1.1*inch, fill=1)
  c.setFillColor(black)
  c.drawString(-0.6*inch, 9.1*inch, h1)
  c.drawString(0.4*inch, 8.7*inch, h2)

def historia_med_pdf(request, id_emergencia):
  # Create the HttpResponse object with the appropriate PDF headers.
  response = HttpResponse(content_type='application/pdf')
  response['Content-Disposition'] = 'filename="historia.pdf"'

  # Create the PDF object, using the response object as its "file."
  c = canvas.Canvas(response)

  header_pdf(c, "Historial Médico", "Electrónico")

  emer  = get_object_or_404(Emergencia,id=id_emergencia)
  c.setFont("Helvetica", 8)
  datos = "Paciente: " + emer.paciente.apellidos +", " +emer.paciente.nombres + ", C.I. "+ emer.paciente.cedula 
  c.drawString(200, 9.4*inch, datos)
  c.drawString(200, 9.2*inch, "Edad: " + str(emer.paciente.edad()))
  
  #Consultas necesarias para la historia medica
  ingreso = datetime.now()
  atList = Atencion.objects.filter(emergencia=id_emergencia)
  atList2 = atList[0]
  medicamento = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo = "medicamento")
  
  #Consultas de informacion para la Historia Medica 
  triageList = Triage.objects.filter(emergencia=id_emergencia).order_by("-fechaReal")
  triage = triageList[0]

  #Enfermedad Actual 
  enfA = EnfermedadActual.objects.get(atencion=atList[0].id)
  
  #Antecedentes
  ant = Pertenencia.objects.filter(paciente=emer.paciente)

  #Examen Fisico
  #No se aun

  #Diagnostico Definitivo 
  diags = Diagnostico.objects.filter(atencion=atList2)

  #Indicaciones
  dietaList = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo = "dieta")
  dieta = dietaList[0]
  hidList = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo = "hidrata")
  hidrata = hidList[0]
  lab = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo = "lab")
  img = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo = "imagen")
  endList = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo = "endoscopico")
  endos = endList[0]
  medicamento = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo = "medicamento")

  ####################### Informacion de la Historia ##########################
  c.setFont("Helvetica", 10)
  c.drawString(-0.3*inch, 8*inch, "Medico Responsable: " + str(emer.responsable.cedula))
  

  #Modulo de Triage 
  # choose some colors
  c.setStrokeColor(lightblue)                  #borde del rectangulo
  c.setFillColor(lightblue)                         #color de fondo
  # draw a rectangle
  c.rect(-inch,7.5*inch,6*inch,0.3*inch, fill=1)
  c.setFillColor(black)
  c.setFont("Helvetica", 12)
  c.drawString(0.5*inch, 7.6*inch, "Modulo de Triage")
  c.drawString(2.5*inch, 7.6*inch, "NIVEL" + str(triage.nivel))
  c.setFont("Helvetica", 10)
  c.drawString(-0.3*inch, 7.3*inch, "Fecha y hora de ingreso: " + str(triage.fechaR()))
  c.drawString(-0.3*inch, 7.1*inch, "Recursos que necesita: " + str(triage.recursos))
  c.drawString(-0.3*inch, 6.9*inch, "Motivo de Ingreso: " + str(triage.motivo))
  c.drawString(-0.3*inch, 6.7*inch, "Temperatura: " + str(triage.signos_tmp) + "° centigrados")
  c.drawString(-0.3*inch, 6.5*inch, "Frecuencia Cardíaca: " + str(triage.signos_fc) + " por minuto") 
  c.drawString(-0.3*inch, 6.3*inch, "Frecuencia Respiratoria: " + str(triage.signos_fr) + " por minuto") 
  c.drawString(-0.3*inch, 6.1*inch, "Presion Sistolica: " + str(triage.signos_pa) + " mmHg")
  c.drawString(-0.3*inch, 5.9*inch, "Presion Diastolica: " + str(triage.signos_pb) + " mmHg")
  c.drawString(-0.3*inch, 5.7*inch, "Sturacion de Oxigeno: " + str(triage.signos_saod) + "%")
  c.drawString(-0.3*inch, 5.5*inch, "Escala AVPU: " + str(triage.signos_avpu))
  c.drawString(-0.3*inch, 5.3*inch, "Dolor: " + str(triage.signos_dolor))

  #Modulo de Atencion
  c.setStrokeColor(lightblue)                  #borde del rectangulo
  c.setFillColor(lightblue)  
  c.rect(-inch,4.8*inch,6*inch,0.3*inch, fill=1)
  c.setFillColor(black)
  c.setFont("Helvetica", 12)
  c.drawString(0.5*inch, 4.9*inch, "Modulo de Atencion en el Departamento de Emergencia")
  c.setFont("Helvetica", 10)
  c.drawString(-0.3*inch, 4.6*inch, "Fecha y hora de atencion: " + str(atList2.fechaReal))
  c.drawString(-0.3*inch, 4.4*inch, "Area de la Atencion: " + str(triage.areaAtencion))
  c.drawString(-0.3*inch, 4.2*inch, "Enfermedad Actual: " + str(enfA.narrativa))
  c.drawString(-0.3*inch, 4*inch, "Antecedentes: ")
  i = 3.8
  for a in ant:
    c.drawString(-0.1*inch, i*inch, str(a.antecedente)) 
    i = i - 0.2
  
  c.drawString(-0.3*inch,i*inch, "Indicaciones: ")
  c.drawString(-0.1*inch,(i-0.2)*inch, "Dieta: " + dieta.indicacion.nombre)
  c.drawString(-0.1*inch,(i-0.4)*inch, "Hidratacion: " + hidrata.indicacion.nombre)
  c.drawString(-0.1*inch,(i-0.6)*inch, "Laboratorio: ")

  i = i - 0.8
  for l in lab:
    c.drawString(-0.01*inch,i*inch, l.indicacion.nombre)
    i = i - 0.2    

  c.drawString(-0.1*inch,i*inch, "Imagenologias: ")

  i = i - 0.2
  for im in img:
    c.drawString(-0.01*inch,i*inch, im.indicacion.nombre)
    i = i - 0.2    

  c.drawString(-0.3*inch,(i-0.2)*inch, "Diagnostico Final: ")

  i = i - 0.4 
  for d in diags:
    c.drawString(-0.01*inch,i*inch, d.enfermedad.descripcion)
    i = i - 0.2

  # Close the PDF object cleanly, and we're done.
  c.showPage()
  c.save()
  return response

def constancia_pdf(request, id_emergencia):
  # Create the HttpResponse object with the appropriate PDF headers.
  response = HttpResponse(content_type='application/pdf')
  response['Content-Disposition'] = 'filename="constancia.pdf"'

  # Create the PDF object, using the response object as its "file."
  c = canvas.Canvas(response)

  header_pdf(c, "Constancia de", "Atención")

  emer  = get_object_or_404(Emergencia,id=id_emergencia)
  atList = Atencion.objects.filter(emergencia=id_emergencia)
  atList2 = atList[0]
  diags = Diagnostico.objects.filter(atencion=atList2)
  medicamento = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo = "medicamento")
  ingreso = datetime.now()
  #Consultas de informacion para la Historia Medica 
  triageList = Triage.objects.filter(emergencia=id_emergencia).order_by("-fechaReal")
  triage = triageList[0]


  c.setFont("Helvetica", 12)
  c.drawString(0.6*inch, 8*inch," Por medio de la presente se hace constar que el paciente "+ emer.paciente.nombres )
  c.drawString(0.4*inch, 7.8*inch, emer.paciente.apellidos + ", titular de la cedula de identidad " + str(emer.paciente.cedula) + ", acudio al Centro Medico de")
  c.drawString(0.4*inch, 7.6*inch, "Caracas el dia de hoy al presentar: ")
  i = 7.4
  if diags:
    for d in diags:
      if d:
        i = i-0.2
        c.drawString(0.6*inch, i*inch,d.enfermedad.descripcion)

 # c.drawString(0.4*inch, (i-0.4)*inch,"Se le indico tratamiento medico ambulatorio")
  if triage.fechaR == None:
    c.drawString(0.4*inch, (i-0.6)*inch, "Fecha: " +str(datetime.now().strftime("%d/%m/%y a las %H:%M:%S")))
  else:
    c.drawString(0.4*inch, (i-0.6)*inch, "Fecha: " +str(triage.fechaReal.strftime("%d/%m/%y a las %H:%M:%S")))

  c.drawString(0.4*inch, (i-1.1)*inch, "Atentamente, ")
  c.drawString(0.4*inch, (i-1.3)*inch, emer.responsable.last_name + ", " + emer.responsable.first_name)
  c.drawString(0.4*inch, (i-1.5)*inch, "C.I.N. " + str(emer.responsable.cedula))

  c.showPage()
  c.save()
  return response

def indicaciones_pdf(request, id_emergencia):
  # Create the HttpResponse object with the appropriate PDF headers.
  response = HttpResponse(content_type='application/pdf')
  response['Content-Disposition'] = 'filename="indicaciones.pdf"'

  # Create the PDF object, using the response object as its "file."
  c = canvas.Canvas(response)

  header_pdf(c, "Reporte de", "Indicaciones")

  #Consultas necesarias para el reporte de indicaciones
  emer  = get_object_or_404(Emergencia,id=id_emergencia)
  ingreso = datetime.now()
  indicaciones = Asignar.objects.filter(emergencia = id_emergencia)

  c.setFont("Helvetica", 12)
  c.drawString(3*inch, 9.3*inch, "Medico Responsable: " + emer.responsable.last_name + ", " + emer.responsable.first_name)
  c.drawString(3*inch, 9.1*inch, "C.I.N. " + str(emer.responsable.cedula))
  c.drawString(0.4*inch, 8*inch, "Paciente: " + emer.paciente.apellidos + ", " + emer.paciente.nombres)
  c.drawString(0.4*inch, 7.8*inch, "C.I.N. " + str(emer.paciente.cedula))

  data = []
  tipos = ["Tipo"]
  nombres = ["Nombre"]
  status = ["Estado Actual"]
  for i in indicaciones:
    if i.indicacion.tipo == "dieta":
      tipos.append("Dieta")
    elif i.indicacion.tipo == "hidrata":
      tipos.append("Hidratacion")
    elif i.indicacion.tipo == "medicamento":
      tipos.append("Medicamento")
    elif i.indicacion.tipo == "lab":
      tipos.append("Diagnostico-Laboratorio")
    elif i.indicacion.tipo == "imagen":
      tipos.append("Diagnostico-Imagenologia")
    elif i.indicacion.tipo == "endoscopia":
      tipos.append("Diagnostico-Estudio Endoscopico")
    elif i.indicacion.tipo == "valora":
      tipos.append("Diagnostico-Valoracion Especializada")
    elif i.indicacion.tipo == "otros":
      tipos.append("Diagnostico-Otros")
    elif i.indicacion.tipo == "terapeutico":
      tipos.append("Terapeutico")

    nombres.append(i.indicacion.nombre)
    status.append(i.statusA())

  data.append(tipos)
  data.append(nombres)
  data.append(status)
  data = zip(*data)
  table=Table(data, colWidths=2.25*inch, rowHeights=20)
  table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-len(tipos)),lightblue), ('ALIGN',(0,0),(-1,-1),'CENTER'),
    ('INNERGRID', (0,0), (-1,-1), 0.25, black), ('BOX', (0,0), (-1,-1), 0.25, black),
    ('FONTSIZE', (0,0), (-1,-len(tipos)), 14)]))
  table.wrapOn(c, 200, 400)
  table.drawOn(c,-0.2*inch,6*inch)

  c.showPage()
  c.save()
  return response


def reporte_triage_pdf(request, idP):
  # Create the HttpResponse object with the appropriate PDF headers.
  response = HttpResponse(content_type='application/pdf')
  response['Content-Disposition'] = 'filename="triage.pdf"'

  # Create the PDF object, using the response object as its "file."
  c = canvas.Canvas(response)

  p = get_object_or_404(Paciente,pk=idP)
  emer = Emergencia.objects.filter(paciente=p)
  emer = emer[len(emer)-1]  #obtengo la ultima posicion de la lista, es el triage mas reciente
  es = Emergencia.objects.filter(paciente=p) #lista de emergencias del paciente
  triage = emer.triages()
  header_pdf(c, "Evaluación de", "Triage")
  t = triage[len(triage)-1]
  
  i = 8  
  c.setFont("Helvetica", 14)
  c.drawString(-0.3*inch, i*inch, "Datos de Identificación" )
  c.drawString(3.5*inch, i*inch, "Signos Vitales ")
    
  c.setFont("Helvetica", 10)
  i = i-0.3 
  c.drawString(-0.3*inch, i*inch, "Nombre:  " + emer.paciente.apellidos +", " +emer.paciente.nombres )
  i = i-0.2 
  c.drawString(-0.3*inch, i*inch, "C.I.:  "+ emer.paciente.cedula )
  i = i-0.2 
  c.drawString(-0.3*inch, i*inch, "Sexo:  "+ emer.paciente.sexoR() )
  i = i-0.2 
  c.drawString(-0.3*inch, i*inch, "Edad:  " + str(emer.paciente.edad()))
  i = i-0.5 
  c.drawString(-0.3*inch, i*inch, "NIVEL DE TRIAGE:  " + str(t.nivel))
  
  i = 8 -0.3 
  c.drawString(3.5*inch, i*inch, "Temperatura:  " + str(t.signos_tmp) + " °C")
  i = i -0.2
  c.drawString(3.5*inch, i*inch, "Tensión Arterial:  " + str(t.signos_pb) + " / " + str(t.signos_pa) + " mmHg")
  i = i -0.2
  c.drawString(3.5*inch, i*inch, "Frecuencia Cardíaca:  " + str(t.signos_fc) + " ppm") 
  i = i -0.2
  c.drawString(3.5*inch, i*inch, "Frecuencia Respiración:  " + str(t.signos_fr) + " ppm") 
  i = i -0.2
  c.drawString(3.5*inch, i*inch, "Saturación Oxígeno:  " + str(t.signos_saod) + " %")
  i = i -0.2
  c.drawString(3.5*inch, i*inch, "AVPU:  " + str(t.signos_avpu))
  i = i -0.2
  c.drawString(3.5*inch, i*inch, "Dolor:  " + str(t.signos_dolor))
  
  i = i -0.4
  c.drawString(-0.3*inch, i*inch, "Atendido:  " + str(t.fechaReal.strftime("%d/%m/%y a las %H:%M")))
  c.drawString(3.5*inch, i*inch, "Medico: " + t.medico.last_name + ", " + t.medico.first_name)
  
  c.showPage()
  c.save()
  return response
