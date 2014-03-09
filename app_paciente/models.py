# -*- encoding: utf-8 -*-

from django.db import models
from django.utils import timezone


SEXO = (
    (1,'Masculino'),
    (2,'Femenino'),
)

RELACION = (
    (1,'Esposo/a'),
    (2,'Pareja'),
    (3,'Papa'),
    (4,'Mama'),
    (5,'Hermano/a'),
    (6,'Familiar'),
    (7,'Amigo/a'),
    (8,'Entorno Laboral'),
    (9,'Conocido'),
    (10,'Misma Comunidad'),
    (11,'No hay nexo'),
)

# Create your models here.
class Enfermedad(models.Model):
    id =  models.CharField(max_length= 10, primary_key=True)
    descripcion = models.CharField(max_length= 400)
    grupo = models.CharField(max_length=200, blank=True, null=True)
    def __unicode__(self):
        return "%s" % (self.descripcion)
        
class Paciente(models.Model):
    cedula = models.TextField(unique = True, default = 0)
    nombres = models.CharField(max_length = 64)
    apellidos = models.CharField(max_length = 64)
    sexo = models.IntegerField(choices = SEXO)
    fecha_nacimiento = models.DateField()
    tlf_cel = models.CharField(max_length = 11)
    email = models.CharField(max_length = 64)
    direccion = models.CharField(max_length = 128)
    tlf_casa = models.CharField(max_length = 11)

    contacto_rel = models.IntegerField(choices = RELACION)
    contacto_nom = models.CharField(max_length = 64)
    contacto_tlf = models.CharField(max_length = 11)

    foto = models.ImageField(upload_to = "/home/jlego/tds-gense/media/img/pacientes",blank = True)
    signos_tmp = models.FloatField(default = 0,blank = True)
    signos_fc = models.FloatField(default = 0,blank = True)
    signos_fr = models.IntegerField(default = 0,blank = True)
    signos_pa = models.IntegerField(default = 0,blank = True)
    signos_pb = models.IntegerField(default = 0,blank = True)
    signos_saod = models.FloatField(default = 0,blank = True)
    enfermedades = models.ManyToManyField(Enfermedad, blank = True)
    def __unicode__(self):

        return "%s, %s" % (self.apellidos,self.nombres)

    def edad(self):
        edad = timezone.datetime.now().year - self.fecha_nacimiento.year
        mes = timezone.datetime.now().month - self.fecha_nacimiento.month
        if mes < 0:
            edad = edad -1
        elif mes == 0:
            dia = timezone.datetime.now().day - self.fecha_nacimiento.day
            if dia < 0:
                edad = edad -1
        return edad

    def meses(self):
        meses = (timezone.datetime.now().year - self.fecha_nacimiento.year)*12
        mes = timezone.datetime.now().month - self.fecha_nacimiento.month
        dia = timezone.datetime.now().day - self.fecha_nacimiento.day
        if dia < 0:
            mes = - 1
        meses = meses + mes        
        return abs(meses)

    def sexoR(self):
        resp = "Hombre"
        if (self.sexo == 2):
            resp = "Mujer"
        return resp

    def relacion(self):
        relaciones = [i[1] for i in RELACION if i[0] == self.contacto_rel]
        relacion = relaciones[0]
        return relacion

    def src_foto(self):
        resp = "/static/img/pacientes/hombre.png"
        if self.foto:
            resp="/foto/real"
        else:
            if (self.sexo == 2):
                resp = "/static/img/pacientes/mujer.png"
        return resp
                
class Antecedente(models.Model):
    tipo   = models.CharField(max_length=64)
    nombre = models.CharField(max_length=64)
    def __unicode__(self):
        return "%s" % (self.nombre)


class Pertenencia(models.Model):
    paciente    = models.ForeignKey(Paciente)
    antecedente = models.ForeignKey(Antecedente)
    def __unicode__(self):
        return "%s-%s" % (self.paciente.nombres,self.antecedente.nombre)
    
    def fechaR(self):
        result = Fecha.objects.filter(pertenencia=self)
        if result:
            return "%s" %(result[0].fecha)
        else: 
            return "%s" % ("no hay fecha")
    
    def lugarR(self):
        result = Lugar.objects.filter(lugarpertenencia__pertenencia=self)
        if result:
            return "%s" %(result[0].nombre)
        else: 
            return "%s" % ("no hay lugar")
    
    def tratamientoR(self):
        result = Tratamiento.objects.filter(tratamientopertenencia__pertenencia=self)
        if result:
            return "%s" %(result[0].nombre)
        else: 
            return "%s" % ("no hay tratamiento")
        
class Lugar(models.Model):
    nombre = models.CharField(max_length=64)

class LugarPertenencia(models.Model):
    pertenencia = models.ForeignKey(Pertenencia)
    lugar       = models.ForeignKey(Lugar)

class Tratamiento(models.Model):
    nombre = models.CharField(max_length=64)
    
class TratamientoPertenencia(models.Model):
    pertenencia = models.ForeignKey(Pertenencia)
    tratamiento = models.ForeignKey(Tratamiento)

class Fecha(models.Model):
    fecha       = models.IntegerField(default=2013,blank=True)
    pertenencia = models.ForeignKey(Pertenencia)
