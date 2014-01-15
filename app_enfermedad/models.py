from django.db import models
from app_emergencia.models import Atencion


REVISADO = (
    ('0','no'),
    ('1','si'),
)

# Create your models here.

class ParteCuerpo(models.Model):
    nombre = models.CharField(max_length=48)
    def __unicode__(self):
        return "%s" % (self.nombre)

class ZonaCuerpo(models.Model):
    nombre = models.CharField(max_length=48)
    def __unicode__(self):
        return "%s" % (self.nombre)

class Aspecto(models.Model):
    nombre = models.CharField(max_length=48)
    def __unicode__(self):
        return "%s" % (self.nombre)

class AspectoAtencion(models.Model):
    revisado = models.CharField(max_length=1,choices=REVISADO)
    aspecto  = models.ForeignKey(Aspecto)
    atencion = models.ForeignKey(Atencion)
    def __unicode__(self):
        return "%s" % (self.aspecto.nombre)
    def partecuerpoR(self):
        result = ParteAspecto.objects.filter(aspecto=self.aspecto)
        if result:
            return "%s" %(result[0].partecuerpo.nombre)
        else: 
            return "%s" % ("no hay parte del cuerpo")
    def estadoR(self):
        result = Anomalia.objects.filter(aspectoatencion=self)
        if result:
            return "anormal"
        elif self.revisado == '1': 
            return "normal"
        else:
            return 'no'
    def anomaliaR(self):
        result = Anomalia.objects.filter(aspectoatencion=self)
        if result:
            return "%s" %(result[0].descripcion)
        else: 
            return "%s" % ("")

class Anomalia(models.Model):
    descripcion = models.CharField(max_length=48)
    aspectoatencion = models.ForeignKey(AspectoAtencion)
    def __unicode__(self):
        return "%s" % (self.aspectoatencion.aspecto.nombre)

class ZonaParte(models.Model):
    partecuerpo = models.ForeignKey(ParteCuerpo)
    zonacuerpo  = models.ForeignKey(ZonaCuerpo)

class ParteAspecto(models.Model):
    aspecto     = models.ForeignKey(Aspecto)
    partecuerpo = models.ForeignKey(ParteCuerpo)
    def __unicode__(self):
        return "%s-%s" % (self.aspecto.nombre,self.partecuerpo.nombre)
