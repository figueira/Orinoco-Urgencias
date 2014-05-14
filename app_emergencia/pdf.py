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

def header1_pdf(c):
  # move the origin up and to the left
  c.translate(inch,inch)
  # define a large font
  c.drawInlineImage("static/img/logoazul.png", -50,700, width=40, height=60)
  c.setFont("Helvetica", 8)
  c.drawString(10, 740,"Centro Medico de Caracas")
  c.drawString(10, 730, "Av. Eraso, Plaza El Estanque")
  c.drawString(10, 720, "Urb. San Bernardino, Caracas, Venezuela")
  c.drawString(10, 710, "Tel. 58+ 212-555-9111 / 555-9486 / 552-2222")

def header_pdf(c,h1,h2):
  header1_pdf(c)
   
  c.setFont("Helvetica", 22)
  # choose some colors
  c.setStrokeColor(lightblue)                  #borde del rectangulo
  c.setFillColor(lightblue)                         #color de fondo
  # draw a rectangle
  c.rect(-inch,8.4*inch,3.7*inch,1.1*inch, fill=1)
  c.setFillColor(black)
  c.drawString(-0.5*inch, 9.1*inch, h1)
  c.drawString(0.5*inch, 8.7*inch, h2)
  
# chequea si se debe agregar una pagina mas al pdf despues de restar 
def restar(c,i,x):
  i = i-x 
  if i <= 0:
    c.showPage()	
    header1_pdf(c)
    c.setFont("Helvetica", 10)
    return 9.4
  else:
    return i

def historia_med_pdf(request, id_emergencia):
  # Create the HttpResponse object with the appropriate PDF headers.
  response = HttpResponse(content_type='application/pdf')
  response['Content-Disposition'] = 'filename="historia.pdf"'

  # Create the PDF object, using the response object as its "file."
  c = canvas.Canvas(response)

  header_pdf(c, "Historial Médico", "Electrónico")
  
  # Consultas de informacion para la Historia Medica 
  emer  = get_object_or_404(Emergencia,id=id_emergencia)  	# Emergencia
  triage = emer.triages()
  t = triage[len(triage)-1]		# Triaje
  atList = Atencion.objects.filter(emergencia=id_emergencia)	# Lista Atencion
  aten = atList[0]	# Atencion
    
  # Fechar y hora de llegada
  c.setFont("Helvetica", 10)
  c.drawString(3*inch, 9.2*inch, "Fecha: " +  str(emer.hora_ingresoReal.strftime("%d/%m/%y")))
  c.drawString(3*inch, 8.9*inch, "Hora de Llegada: " + str(emer.hora_ingresoReal.strftime("%H:%M")))
    
  # SECCION DATOS DEL PACIENTE
  i = 7.5 
  c.setStrokeColor(lightblue)                  #borde del rectangulo
  c.setFillColor(lightblue)                    #color de fondo
  c.rect(-inch,i*inch,6*inch,0.3*inch, fill=1)
  c.setFillColor(black)  					   # colorear letras en negro otra vez
  c.setFont("Helvetica-Bold", 14)
  i = i+0.08
  c.drawString(-0.3*inch, i*inch, "Datos del Paciente" )
    
  c.setFont("Helvetica", 10)
  i = i-0.42 
  c.drawString(-0.3*inch, i*inch, "Nombre:  " + emer.paciente.nombres + " " + emer.paciente.apellidos )
  i = i-0.2 
  c.drawString(-0.3*inch, i*inch, "C.I.:  "+ emer.paciente.cedula )
  c.drawString(1.5*inch, i*inch, "Sexo:  "+ emer.paciente.sexoR() )
  c.drawString(3.2*inch, i*inch, "Edad:  " + str(emer.paciente.edad()))
  i = i-0.2 
  c.drawString(-0.3*inch, i*inch, "Nombre del Medico:   " + emer.responsable.first_name + " " + emer.responsable.last_name)
  
  
  #  SECCION MODULO DE ATENCION
  i = i-0.8	
  c.setStrokeColor(lightblue)                  #borde del rectangulo
  c.setFillColor(lightblue)                    #color de fondo
  c.rect(-inch,i*inch,6*inch,0.3*inch, fill=1)
  c.setFillColor(black)  					   # colorear letras en negro otra vez
  c.setFont("Helvetica-Bold", 14)
  i = i+0.08
  c.drawString(-0.3*inch, i*inch, "Modulo de Atencion" )
  
  c.setFont("Helvetica", 10)
  i = i-0.42   
  c.drawString(-0.3*inch, i*inch, "Nivel de Triage:  " + str(t.nivel)) 
  c.drawString(1.5*inch, i*inch, "Motivo de Consulta:  " + str(t.motivo))
  
  
  
  #		ENFERMEDAD ACTUAL
  i = i-0.4 
  c.setFont("Helvetica-Bold", 11)
  c.drawString(-0.3*inch, i*inch, "I. Enfermedad Actual:  ")  
  # busco info en BD
  enfA = EnfermedadActual.objects.get(atencion=aten.id)  
  i= i-0.2
  c.setFont("Helvetica", 10)
  c.drawString(0*inch, i*inch, enfA.narrativa)
  
  
  
  #		ANTECEDENTES   A partir de aqui se resta chequeando para una nueva hoja
  i =  restar(c,i,0.4) 
  c.setFont("Helvetica-Bold", 11)
  c.drawString(-0.3*inch, i*inch, "II. Antecedentes:  ")

  # medicos
  antMed = Pertenencia.objects.filter(paciente=emer.paciente, antecedente__tipo = "medica")	  	 # busco info en BD
  i= restar(c,i,0.2)
  c.setFont("Helvetica", 11)
  c.drawString(0*inch, i*inch, "- Medicos:")
  c.setFont("Helvetica", 10)  
  if len(antMed) > 0:
    for a in antMed: 
        i=restar(c,i,0.2)
        c.drawString(0.3*inch, i*inch, str(a.antecedente))
  else:
    c.drawString(0.8*inch, i*inch, "No existen")

  # quirurgicos  
  antQui = Pertenencia.objects.filter(paciente=emer.paciente, antecedente__tipo = "quirurgica")	 # busco info en BD
  i=restar(c,i,0.3)
  c.setFont("Helvetica", 11)
  c.drawString(0*inch, i*inch, "- Quirurgicos:")
  c.setFont("Helvetica", 10)  
  if len(antQui) > 0:
    for a in antQui: 
        i=restar(c,i,0.2)
        c.drawString(0.3*inch, i*inch, str(a.antecedente))
  else:
    c.drawString(1*inch, i*inch, "No existen")
	
  # alergicos  
  antAler = Pertenencia.objects.filter(paciente=emer.paciente, antecedente__tipo = "alergia")	 # busco info en BD
  i=restar(c,i,0.3)
  c.setFont("Helvetica", 11)
  c.drawString(0*inch, i*inch, "- Alergicos:")
  c.setFont("Helvetica", 10)  
  if len(antAler) > 0:
    for a in antAler: 
        i=restar(c,i,0.2)
        c.drawString(0.3*inch, i*inch, str(a.antecedente))
  else:
    c.drawString(0.9*inch, i*inch, "No existen")


  
  #		EXAMEN FISICO
  i =restar(c,i,0.4)
  c.setFont("Helvetica-Bold", 11)
  c.drawString(-0.3*inch, i*inch, "III. Examen Fisico:  ")
  i=restar(c,i,0.2)
  c.setFont("Helvetica", 11)
  c.drawString(0*inch, i*inch, "Signos Vitales:  ")
  i=restar(c,i,0.2)
  c.setFont("Helvetica", 10)
  c.drawString(0.3*inch, i*inch, "Ta:  " + str(t.signos_pb) + " / " + str(t.signos_pa) + " mmHg")
  c.drawString(2.0*inch, i*inch, "Pulso:  " + str(t.signos_fc) + " ppm") 
  c.drawString(3.6*inch, i*inch, "Resp:  " + str(t.signos_fr) + " ppm") 
  c.drawString(5*inch, i*inch, "Temp:  " + str(t.signos_tmp) + " °C")
  i =restar(c,i,0.2)
  c.drawString(0.3*inch, i*inch, "Sat. Oxí.:  " + str(t.signos_saod) + " %")
  c.drawString(2.0*inch, i*inch, "AVPU:  " + str(t.signos_avpu))
  c.drawString(3.6*inch, i*inch, "Dolor:  " + str(t.signos_dolor))
  
  # busco info en BD
  examen = AspectoAtencion.objects.filter(atencion=aten, revisado = "1")	# Lista Atencion
  examen = list(examen)
  examen.sort(key=lambda x: x.partecuerpoR())	# ordeno por parte del cuerpo

  parteCuerpo = ""  
  for e in examen:
    if parteCuerpo != e.partecuerpoR():
      i= restar(c,i,0.3)
      c.setFont("Helvetica", 11)
      c.drawString(0*inch, i*inch,  e.partecuerpoR().replace ("_", " ").title() + ":")
      parteCuerpo = e.partecuerpoR()
	  
    i= restar(c,i,0.2)
    c.setFont("Helvetica", 10)
    c.drawString(0.3*inch, i*inch,  e.aspecto.nombre)
    
    if e.estadoR() == "anormal":
      c.drawString(3.5*inch, i*inch,  "Alterado:")
      c.drawString(4.15*inch, i*inch,  e.anomaliaR())
    else:
      c.drawString(3.5*inch, i*inch,  e.estadoR().title())

 
 
  #		EXAMENES COMPLEMENTARIOS
  i =restar(c,i,0.4)
  c.setFont("Helvetica-Bold", 11)
  c.drawString(-0.3*inch, i*inch, "IV. Examenes Complementarios:  ")
  
  # Indicaciones diagnosticas
  ind = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo__in = ["lab", "imagen", "endoscopico", "otros", "valora"] ).order_by("indicacion__tipo") 	# busco info en BD
  tipo_ind = ""
  if len(ind) > 0:
	i=i+0.1
	for l in ind: 
		if tipo_ind != l.indicacion.tipo:
			tipo_ind = l.indicacion.tipo
			i=restar(c,i,0.3)
			c.setFont("Helvetica", 11)
			if tipo_ind == "lab":				
				c.drawString(0*inch, i*inch, "- Laboratorios:")
			elif tipo_ind == "imagen":
				c.drawString(0*inch, i*inch, "- Imagenologia:")
			elif tipo_ind == "endoscopico":
				c.drawString(0*inch, i*inch, "- Estudios Especiales:")
			elif tipo_ind == "valora":
				c.drawString(0*inch, i*inch, "- Valoracion Especializada:")
			elif tipo_ind == "otros":
				c.drawString(0*inch, i*inch, "- Otros:")
			
		c.setFont("Helvetica", 10)  
		i=restar(c,i,0.2)
		frase = l.indicacion.nombre
		
		if tipo_ind == "imagen":
			part = EspImg.objects.filter(asignacion = l)
			if len(part) > 0 and part[0].parte_cuerpo != '':
				frase = frase + ":  " + part[0].parte_cuerpo
				
		c.drawString(0.3*inch, i*inch, frase)
  else:
    c.setFont("Helvetica", 10)  
    c.drawString(2.15*inch, i*inch, "No se realizo ningun examen")
    
	
	
  #		IMPRESION DIAGNOSTICA
  i =restar(c,i,0.4)
  c.setFont("Helvetica-Bold", 11)
  c.drawString(-0.3*inch, i*inch, "V. Impresion Diagnostica:  ")	
  
  # busco en BD
  diags = Diagnostico.objects.filter(atencion=aten)
  c.setFont("Helvetica", 10)  
  if len(diags) > 0:
    for d in diags: 
        i=restar(c,i,0.2)
        c.drawString(0*inch, i*inch, "- " + str(d.enfermedad.descripcion))
  
  
  
  #		INDICACIONES
  i =restar(c,i,0.4)
  c.setFont("Helvetica-Bold", 11)
  c.drawString(-0.3*inch, i*inch, "VI. Indicaciones:  ")	
  
  # Indicaciones diagnosticas
  # dieta
  dieta = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo = "dieta") 	# busco info en BD
  if len(dieta) > 0:  
	dieta = dieta[0]
	i=restar(c,i,0.3)
	c.setFont("Helvetica", 11)
	c.drawString(0*inch, i*inch, "- Dieta:")		
	c.setFont("Helvetica", 10)  
	i=restar(c,i,0.2)
	c.drawString(0.3*inch, i*inch, dieta.indicacion.nombre + ".  " +  dieta.dieta_OB())
	
	
  # hidratacion
  hidrata = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo= "hidrata") 	# busco info en BD
  if len(hidrata) > 0: 
	hidrata = hidrata[0]
	i=restar(c,i,0.3)
	c.setFont("Helvetica", 11)
	c.drawString(0*inch, i*inch, "- Hidratacion:")
	temp = EspHidrata.objects.filter(asignacion = hidrata)[0]
	comp = CombinarHidrata.objects.filter(hidratacion1 = temp)
	c.setFont("Helvetica", 10)  
	i=restar(c,i,0.2)
	if len(comp) > 0:
		c.drawString(0.3*inch, i*inch, str(temp.volumen) + "cc de " + hidrata.indicacion.nombre + " combinado con " + comp[0].hidratacion2.nombre + " a " + str(temp.vel_infusion) + " gotas/min.")
	else:
		c.drawString(0.3*inch, i*inch, str(temp.volumen) + "cc de " + hidrata.indicacion.nombre + " a " + str(temp.vel_infusion) + " gotas/min.")
		
	if temp.complementos !="":	
		i=restar(c,i,0.2)
		c.drawString(0.3*inch, i*inch, "Complementos: " + (temp.complementos))
  
  # medicamento
  med = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo= "medicamento") 	# busco info en BD
  if len(med) > 0: 
	i=restar(c,i,0.3)
	c.setFont("Helvetica", 11)
	c.drawString(0*inch, i*inch, "- Medicamento:")
	c.setFont("Helvetica", 10) 
	for m in med:		 
		i=restar(c,i,0.2)
		c.drawString(0.3*inch, i*inch, str(m.med_Dosis()) + m.med_Conc() + " de " + m.indicacion.nombre + " " + m.med_Frec() + " " + m.med_TFrec() + ". Via " + m.med_Viad())

		
  # el resto de las indicaciones (terapeutico y otras)
  ind = Asignar.objects.filter(emergencia = id_emergencia, indicacion__tipo__in = ["terapeutico", "otras"] ).order_by("indicacion__tipo") 	# busco info en BD
  tipo_ind = ""
  if len(ind) > 0: 
	for l in ind: 
		if tipo_ind != l.indicacion.tipo:
			tipo_ind = l.indicacion.tipo
			i=restar(c,i,0.3)
			c.setFont("Helvetica", 11)
			if tipo_ind == "terapeutico":	
				c.drawString(0*inch, i*inch, "- Terapia:")
			elif tipo_ind == "otras":
				c.drawString(0*inch, i*inch, "- Otras:")
			
		c.setFont("Helvetica", 10)  
		i=restar(c,i,0.2)
		c.drawString(0.3*inch, i*inch, l.indicacion.nombre)


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
  c.drawString(0.0*inch, 7.8*inch," Por medio de la presente se hace constar que el paciente "+ emer.paciente.nombres )
  c.drawString(-0.3*inch, 7.6*inch, emer.paciente.apellidos + ", titular de la cedula de identidad " + str(emer.paciente.cedula) + ", acudio al Centro Medico de")
  c.drawString(-0.3*inch, 7.4*inch, "Caracas el dia de hoy por presentar: ")
  i = 7.2
  if diags:
    for d in diags:
      if d:
        i = i-0.2
        c.drawString(0.0*inch, i*inch,d.enfermedad.descripcion)

  if triage.fechaR == None:
    c.drawString(-0.3*inch, (i-0.6)*inch, "Caracas, " +str(datetime.now().strftime("%d/%m/%y a las %H:%M")))
  else:
    c.drawString(-0.3*inch, (i-0.6)*inch, "Caracas, " +str(triage.fechaReal.strftime("%d/%m/%y a las %H:%M")))

  c.drawString(-0.3*inch, (i-1.1)*inch, "Atentamente, ")
  c.drawString(-0.3*inch, (i-1.3)*inch, "Dr. " + emer.responsable.first_name + " " + emer.responsable.last_name)

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
  indicaciones = Asignar.objects.filter(emergencia = id_emergencia).order_by("fechaReal")

  c.setFont("Helvetica", 10)
  c.drawString(3*inch, 9.2*inch, "Paciente: " + emer.paciente.apellidos + ", " + emer.paciente.nombres)
  c.drawString(3*inch, 9.0*inch, "C.I.: " + str(emer.paciente.cedula))
  c.drawString(3*inch, 8.6*inch, "Medico: " + emer.responsable.first_name + " " + emer.responsable.last_name)
  
  c.setFont("Helvetica-Bold", 14)
  c.drawString(2.4*inch, 7.8*inch, "INDICACIONES")
  

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
    elif i.indicacion.tipo == "endoscopico":
      tipos.append("Diagnostico-Estudios Especiales")
    elif i.indicacion.tipo == "valora":
      tipos.append("Diagnostico-Valoracion Especializada")
    elif i.indicacion.tipo == "otros":
      tipos.append("Diagnostico-Otros")
    elif i.indicacion.tipo == "terapeutico":
      tipos.append("Terapeutico")
    elif i.indicacion.tipo == "otras":
      tipos.append("Otras")

    nombres.append(i.indicacion.nombre)
    status.append(i.statusA())

  data.append(tipos)
  data.append(nombres)
  data.append(status)
  data = zip(*data)
  table=Table(data, colWidths=2.25*inch, rowHeights=0.26*inch)
  table._argW[0]=2.5*inch
  table._argW[2]=2*inch
  c.setFont("Helvetica", 10)
  table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-len(tipos)),lightblue), 
    ('FONT', (0,0), (-1,-len(tipos)), 'Helvetica-Bold'),
    ('ALIGN',(0,0),(-1,-1),'CENTER'),  ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ('INNERGRID', (0,0), (-1,-1), 0.25, black), ('BOX', (0,0), (-1,-1), 0.25, black)]))
  table.wrapOn(c, 200, 400)
  mitad = ((len(indicaciones)+1)*0.26)/2
  dif = 7.5 - mitad
  pos = dif-mitad
  table.drawOn(c,-0.2*inch, pos*inch)
  
  ultIndicacion = indicaciones[len(indicaciones)-1]
  c.drawString(-0.3*inch, (pos-0.8)*inch, "Ultima actualizacion: " + str(ultIndicacion.fechaReal.strftime("%d/%m/%y a las %H:%M:%S")))
  
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
  c.setFont("Helvetica-Bold", 14)
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
  
  i = i -0.6
  c.drawString(-0.3*inch, i*inch, "Atendido:  " + str(t.fechaReal.strftime("%d/%m/%y a las %H:%M")))
  c.drawString(3.5*inch, i*inch, "Medico: " + t.medico.last_name + ", " + t.medico.first_name)
  
  c.showPage()
  c.save()
  return response
