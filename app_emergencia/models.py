# -*- encoding: utf-8 -*-

from django.db import models
from django.db.models import Q
from app_paciente.models import *
from app_usuario.models import * 
from app_enfermedad.models import * 
from math import ceil, floor
from datetime import datetime

# Create your models here.
AEMERGENCIA = (
  ('0','Real'),
  ('1','Referencia'),
)

REALIZADO = (
  ('0','no realizado'),
  ('1','realizado'),
)

ICAUSA = (
  ('0','No Violento'),
  ('1','Colision de Vehiculos'),
  ('2','Arrollamiento'),
  ('3','Herido por Arma Blanca'),
  ('4','Herido por Arma de Fuego'),
  ('5','Caida de Altura'),
  ('6','Intoxicacion'),
  ('7','Efecto Adverso a Medicamento'),
)

AFIRMACION = (
  (0,"No"),
  (1,"Si"),
)

RECURSOS = (
  (0,"Ninguno"),
  (1,"Uno"),
  (2,"Muchos"),
)

AVPU = (
  ("A","A - Alerta y ubicado en espacio y tiempo"),
  ("V","V - Responde ante ordenes verbales"),
  ("P","P - Responde a estimulos doloros"),
  ("U","U - Inconciente"),
)

EDOLOR = (
  (0,"No hay dolor"),
  (1,"1"),
  (2,"2"),
  (3,"3"),
  (4,"4"),
  (5,"5"),
  (6,"6"),
  (7,"7"),
  (8,"8"),
  (9,"9"),
  (10,"10"),
)

# STATUS = (
#   (1,'No Completado'),
#   (2,'Completado'),
# )

class AreaEmergencia(models.Model):
  tipo   = models.CharField(max_length=1,choices=AEMERGENCIA)
  nombre = models.CharField(max_length=48)

  def __unicode__(self):
    return "%s" % self.nombre

class AreaAdmision(models.Model):
  nombre = models.CharField(max_length=48)
  def __unicode__(self):
    return "%s" % self.nombre

class Cubiculo(models.Model):
  nombre = models.CharField(max_length=48)
  area   = models.ForeignKey(AreaEmergencia)

  def __unicode__(self):
    return "%s" % self.nombre

  def esta_asignado(self):
    asignaciones = AsignarCub.objects.filter(cubiculo_id = self.id)
    return asignaciones.count() > 0

class Destino(models.Model):
  nombre = models.CharField(max_length=48)
  def __unicode__(self):
    return "%s" % self.nombre

class Motivo(models.Model):
  nombre = models.CharField(max_length=48)
  def __unicode__(self):
    return "%s" % self.nombre


class Emergencia(models.Model):
  paciente = models.ForeignKey(Paciente)
  responsable = models.ForeignKey(Usuario,related_name = "A cargo")
  ingreso = models.ForeignKey(Usuario,related_name = "Ingresado por")
  hora_ingreso = models.DateTimeField()
  fecha_Esp_act = models.DateTimeField(auto_now_add = True)
  hora_ingresoReal = models.DateTimeField(auto_now_add = True)
  hora_egreso = models.DateTimeField(blank = True,null = True)
  hora_egresoReal = models.DateTimeField(blank = True,null = True)
  egreso = models.ForeignKey(Usuario,
                             related_name = "De alta por",
                             blank = True,
                             null = True)
  destino = models.ForeignKey(Destino,blank = True,null = True)
  
  def __unicode__(self):
    return "%s - %s " % (self.id, self.paciente)

  # Dado un objeto de emergencia, devuelve la lista de causas de eséra que han
  # sido asignadas a ella
  #
  # Salida: Lista de EsperaEmergencia que han sido asignadas a la emergencia
  def esperas_asignadas(self):
    esperas_emergencia = EsperaEmergencia.objects.filter(
                           emergencia = self,
                           hora_fin = None
                         ).order_by('espera__nombre')
    return esperas_emergencia

  # Dado un objeto Emergencia, encuentra todas las causas de espera que aún no 
  # le han sido asignadas
  #
  # Salida: Lista de Espera que aun no han sido asignadas a la emergencia
  def esperas_no_asignadas(self):
    # Aqui calculamos el conjunto de esperas no asignadas eliminando de todas
    # las esperas aquellas que ya estan asignadas
    esperas_asignadas = self.esperas_asignadas()
    esperas_no_asignadas = list(Espera.objects.all().order_by('nombre'))
    for espera_emergencia in esperas_asignadas:
      if espera_emergencia.espera in esperas_no_asignadas:
        esperas_no_asignadas.remove(espera_emergencia.espera)

    return esperas_no_asignadas


  def triages(self):
    triages = Triage.objects.filter(emergencia=self.id).order_by("fechaReal")
    return triages

  def triage(self):
    triage = 0
    triages = self.triages()
    if triages:
      tam = len(triages)
      triage = triages[tam-1].nivel
    return triage

  def fecha_triage(self):
    triages = self.triages()
    fecha = "No se ha tomado signos vitales aún"
    if triages:
      if triages[0].fecha:
        fecha = triages[0].fecha.strftime("%H:%M del %d/%m/%y")
    return fecha

  def atendido(self):
    atendido = False
    atenciones = Atencion.objects.filter(emergencia = self.id)
    if len(atenciones) > 0:
      atendido = True
    return atendido

  def atenciones(self):
    atenciones = Atencion.objects.filter(emergencia=self.id).order_by("fechaReal")
    return atenciones

  def horaR(self):
    return self.hora_ingreso.strftime("%H:%M del %d/%m/%y")
    
  def numEsperasNoAtendidas(self):
    emerEspera = EsperaEmergencia.objects.filter(emergencia=self)
    NoAten = 0
    for esp in emerEspera:
      if esp.estado == '0':
        NoAten = NoAten + 1
    return NoAten
  
  def tiempo_espera(self):
    tiempo = self.hora_ingreso.replace(tzinfo=None)
    tiempo = datetime.now() - tiempo
    return ceil(tiempo.total_seconds())

  def tiempo_espera_causas(self):
    tiempo  = self.fecha_Esp_act.replace(tzinfo=None)
    if self.fecha_Esp_act:    
      tiempo  = datetime.now() - tiempo
    else:
      tiempo  = datetime.now()
    return int(ceil(tiempo.total_seconds()))

  def tiempo_esperaR(self):
    tiempo = self.tiempo_espera()
    dias = int(floor(((tiempo/60)/60)/24))
    tiempo2 = tiempo - (dias*24*60*60)
    horas = int(floor((tiempo2/60)/60))
    tiempo3 = tiempo2 - (horas*60*60)
    minutos = int(floor(tiempo3/60))
    segundos = int(floor(tiempo3%60))    
    return str(dias)+":"+str(horas)+":"+str(minutos)+":"+str(segundos)

  def tiempo_espera_causasR(self):
    tiempo = self.tiempo_espera_causas()
    dias = int(floor(((tiempo/60)/60)/24))
    tiempo2 = tiempo - (dias*24*60*60)
    horas = int(floor((tiempo2/60)/60))
    tiempo3 = tiempo2 - (horas*60*60)
    minutos = int(floor(tiempo3/60))
    segundos = int(floor(tiempo3%60))    
    return str(dias)+":"+str(horas)+":"+str(minutos)+":"+str(segundos)


  def tiempo_emergencia(self):
    tiempo = self.hora_egreso - self.hora_ingreso
    return tiempo.total_seconds()

  def tiempo_emergenciaT(self):
    tiempo = self.hora_egreso - self.hora_ingreso
    return tiempo

  def tiempoEspera(self):
    triages = Triage.objects.filter(emergencia=self.id).order_by("fechaReal")
    if triages:
      t = triages[0].fecha
    else:
      t = self.hora_ingreso
    t = t.replace(tzinfo=None)
    tiempo_actual = datetime.now()
    tiempo = tiempo_actual - t
    return tiempo.total_seconds()

  def tiempoEsperaR(self):
    tiempo = self.tiempoEspera()
    dias = floor(((tiempo/60)/60)/24)
    horas = (tiempo/60)/60
    minutos = (tiempo%60)/60
    segundos = (tiempo%60)%60
    return str(horas)+":"+str(minutos)+":"+str(segundos)

  def cubi(self):
    result = AsignarCub.objects.filter(emergencia=self)
    if result:
      return "%s" %(result[0].cubiculo)
    else: 
      return "%s" % ("NO ASIGNADO")

class AsignarCub(models.Model):
  emergencia = models.ForeignKey(Emergencia)
  cubiculo   = models.ForeignKey(Cubiculo)
  def __unicode__(self):
    return "Emergencia: %s, Cubiculo: %s" % (self.emergencia.id, \
                                             self.cubiculo)

class Espera(models.Model):
  nombre = models.CharField(max_length=48)

  def __unicode__(self):
    return "%s" % self.nombre

  # Retorna la ruta a la imagen que corresponde a la espera
  def url_imagen(self):
    return '/static/img/esperas/espera_' + str(self.id) + '.png'

  # Retorna una reresentacion del objeto en froma de diccionario, para que 
  # pueda ser fácilmente convertido a JSON
  def json_dict(self):
    json = {}
    json['id'] = self.id
    json['nombre'] = self.nombre

    return json

class EsperaEmergencia(models.Model):
  espera = models.ForeignKey(Espera)
  emergencia = models.ForeignKey(Emergencia)
  estado = models.CharField(max_length = 1,choices = REALIZADO)
  # Hora en la que se comienza a contabilizar esa causa de espera para esa
  # emergencia	
  hora_comienzo = models.DateTimeField(auto_now_add = True)
  hora_fin = models.DateTimeField(blank = True, null = True)

  def __unicode__(self):
    return "{0}, {1}, Fin: {3}, Egreso? {4}, Hora egreso: {5}" \
             .format(self.espera.nombre,
                     self.emergencia.paciente,
                     str(self.hora_comienzo),
                     str(self.hora_fin),
                     str(self.emergencia.hora_egreso != None),
                     str(self.emergencia.hora_egreso))

class ComentarioEmergencia(models.Model):
  emergencia = models.ForeignKey(Emergencia)
  comentario = models.CharField(max_length=512)

class Admision(models.Model):
  emergencia     = models.ForeignKey(Emergencia)
  area       = models.ForeignKey(AreaAdmision)
  hora_ingreso   = models.DateTimeField(null=True,blank=True)
  hora_ingresoReal = models.DateTimeField(null=True,blank=True)

class Triage(models.Model):
  emergencia   = models.ForeignKey(Emergencia)
  medico     = models.ForeignKey(Usuario)
  fecha      = models.DateTimeField(blank=True,null=True)
  fechaReal    = models.DateTimeField(auto_now_add=True)
  
  motivo     = models.ForeignKey(Motivo,blank=True)
  areaAtencion   = models.ForeignKey(AreaEmergencia,blank=True)
  ingreso    = models.CharField(max_length=1,blank=True,choices=ICAUSA)
  
  atencion     = models.BooleanField(blank=True)
  esperar    = models.BooleanField(blank=True)
  recursos     = models.IntegerField(choices=RECURSOS,blank=True)
  
  # Valores a tomar
  signos_tmp   = models.FloatField(default=0,blank=True)
  signos_fc    = models.FloatField(default=0,blank=True)
  signos_fr    = models.IntegerField(default=0,blank=True)
  signos_pa    = models.IntegerField(default=0,blank=True)
  signos_pb    = models.IntegerField(default=0,blank=True)
  signos_saod  = models.FloatField(default=0,blank=True)

  # Otros Datos Importantes
  signos_avpu  = models.CharField(max_length=1,blank=True)
  signos_dolor   = models.IntegerField(default=0,blank=True)

  # Resultado de Triage
  nivel      = models.IntegerField()
  def __unicode___(self):
    return "Triaje %s" % self.id

  def fechaR(self):
    self.fecha.strftime("%H:%M del %d/%m/%y")

class ComentarioTriage(models.Model):
  triage = models.ForeignKey(Triage)
  comentario = models.CharField(max_length=512)

class Atencion(models.Model):
  emergencia   = models.ForeignKey(Emergencia)
  medico     = models.ForeignKey(Usuario)
  fecha      = models.DateTimeField()
  fechaReal    = models.DateTimeField(auto_now_add=True)
  area_atencion  = models.CharField(max_length=1)

  def __unicode__(self):
    return "Paciente:%s- Doctor:%s - Area:%s" % (self.emergencia.paciente.apellidos,self.medico.cedula,self.area_atencion)
  def horaA(self):
    return self.fechaReal.strftime("%d/%m/%y a las %H:%M:%S")

# Enfermedad Actual
class EnfermedadActual(models.Model):
  atencion = models.ForeignKey(Atencion)
  narrativa = models.CharField(max_length=512)

# Diagnostico Definitivo
class Diagnostico(models.Model):
  nombreD = models.CharField(max_length=512)
  def __unicode__(self):
    return "%s" % (self.nombreD)

class EstablecerDiag(models.Model):
  atencion = models.ForeignKey(Atencion)
  diagnostico = models.ForeignKey(Diagnostico)
  fecha      = models.DateTimeField()
  fechaReal    = models.DateTimeField(auto_now_add=True)
  def __unicode__(self):
    return "Atencion: %s-Diagnostico: %s" % (self.atencion.id,self.diagnostico.nombreD)
  def horaD(self):
    return self.fechaReal.strftime("%d/%m/%y a las %H:%M:%S")

#----------------------------------Indicacion
class Indicacion(models.Model):
  nombre = models.CharField(max_length=128, blank=False)
  tipo   = models.CharField(max_length=40, blank=False)
  def __unicode__(self):
    # return "TIPO:%s- NOMBRE:%s" % (self.tipo,self.nombre)
    return "%s" % (self.nombre)

class Asignar(models.Model):
  emergencia = models.ForeignKey(Emergencia)
  indicacion = models.ForeignKey(Indicacion)
  persona  = models.ForeignKey(Usuario)
  fecha    = models.DateTimeField()
  fechaReal  = models.DateTimeField()
  status   = models.IntegerField(choices=AFIRMACION)
  
  def __unicode__(self):
    return "Paciente:%s- Nombre:%s- Tipo:%s - Status:%s" % (self.emergencia.paciente.apellidos,self.indicacion.nombre,self.indicacion.tipo,self.status)

  def statusA(self):
    resp = "No Completado"
    if (self.status == 1):
      resp = "Completado"
    return resp

  # def statusA(self):
  #   resp = "No Completado"
  #   if (self.status == 1):
  #     resp = "Completado"
  #   return resp
  
  #------------------------------------- Definiciones para atributos extra:

  # Especificaciones Dieta
  def dieta_OB(self):
    result = EspDieta.objects.filter(asignacion=self)
    if result:
      return "%s" %(result[0].observacion)
    else: 
      return "%s" % ("no hay observacion")
  
  # Especificaciones Medicamento
  # Dosis
  def med_Dosis(self):
    result = EspMedics.objects.filter(asignacion=self)
    if result:
      return "%s" %(result[0].dosis)
    else: 
      return "%s" % ("no hay dosis")

  # Tipo de Concentracion
  def med_Conc(self):
    result = EspMedics.objects.filter(asignacion=self)
    if result:
      return "%s" %(result[0].tipo_conc)
    else: 
      return "%s" % ("no hay asociada un tipo de concentracion")

  # Frecuencia
  def med_Frec(self):
    result = EspMedics.objects.filter(asignacion=self)
    if result:
      return "%s" %(result[0].frecuencia)
    else: 
      return "%s" % ("no hay frec")

  # Tipo de Frecuencia
  def med_TFrec(self):
    result = EspMedics.objects.filter(asignacion=self)
    if result:
      return "%s" %(result[0].tipo_frec)
    else: 
      return "%s" % ("no hay tipo frec")

  # Via de administracion
  def med_Viad(self):
    result = EspMedics.objects.filter(asignacion=self)
    if result:
      return "%s" %(result[0].via_admin)
    else: 
      return "%s" % ("no hay via de administracion")

  # Hora de asignacion
  def horaA(self):
    # Dia y hora
    return self.fechaReal.strftime("%d/%m/%y a las %H:%M:%S")
    # Solo hora
    #return self.fechaReal.strftime("%H:%M:%S")
  
  #--- Para mostrar la informacion adicional cuando el tipo_Frec es SOS:
  # Situacion SOS:
  def med_SOS_sit(self):
    result = EspMedics.objects.filter(asignacion=self)
    result2 = tieneSOS.objects.filter(espMed=result)
    if result2:
      print "que encuentro en situacion: "(result2[0].situacion)
      return "%s" %(result2[0].situacion)
    else: 
      return "%s" % ("NO")
  
  # Comentario SOS:
  def med_SOS_com(self):
    result = EspMedics.objects.filter(asignacion=self)
    result2 = tieneSOS.objects.filter(espMed=result)
    if result2:
      return "%s" %(result2[0].comentario)
    else: 
      return "%s" % ("NO")

# Especificaciones para las indicaciones de Dietas
class EspDieta(models.Model):
  asignacion     = models.ForeignKey(Asignar)
  observacion    = models.CharField(max_length=512,blank=True)
  def __unicode__(self):
    return "Paciente:%s- Observacion:%s" % (self.asignacion.emergencia.paciente.nombres,self.observacion)

# Especificaciones para las indicaciones de Hidratacion
class EspHidrata(models.Model):
  asignacion   = models.ForeignKey(Asignar)
  volumen    = models.IntegerField(blank=True,null=True)
  vel_infusion = models.CharField(max_length=512,blank=True)
  complementos = models.CharField(max_length=512,blank=True)
  def __unicode__(self):
    return "Paciente:%s- DVolumen:%s" % (self.asignacion.emergencia.paciente.apellidos,self.volumen)

# Relacionar dos tipos de solucion
class CombinarHidrata(models.Model):
  hidratacion1 = models.ForeignKey(EspHidrata,null=True)
  hidratacion2 = models.ForeignKey(Indicacion,null=True)

# Especificaciones para las indicaciones de Medicamentos
class EspMedics(models.Model):
  asignacion = models.ForeignKey(Asignar)
  dosis  = models.FloatField(default=0,blank=True)
  tipo_conc = models.CharField(max_length=2,blank=True)
  # mg
  # gr
  # u
  # cc
  frecuencia = models.CharField(max_length=25,blank=True)
  tipo_frec = models.CharField(max_length=4,blank=True)

  # fijo
  # SOS
  via_admin = models.CharField(max_length=13,blank=True)

  # endovenosa
  # subcutanea
  # nebulizacion
  # transdermico
  # rectal
  def __unicode__(self):
    return "Paciente:%s-" % (self.asignacion.emergencia.paciente.apellidos)

# Agrega los detalles extras para el tipo de frecuencia de SOS
class tieneSOS(models.Model):
  espMed    = models.ForeignKey(EspMedics)
  situacion   = models.CharField(max_length=200,blank=True)
  comentario  = models.CharField(max_length=200,blank=True)

# Especificaciones para las indicaciones de Imagenologia
class EspImg(models.Model):
  asignacion    = models.ForeignKey(Asignar)
  parte_cuerpo  = models.CharField(max_length=100,blank=True)
