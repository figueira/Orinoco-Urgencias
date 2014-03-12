# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

SEXO = (
    ('1','Masculino'),
    ('2','Femenino'),
)

USUARIO = (
    ('1','Médico'),
    ('2','Enfermero/a'),
    ('3','Secretario/a'),
)

# Create your models here.
class Usuario(User):
    cedula        = models.IntegerField(default=0, unique=True)
    tipo          = models.CharField(max_length=1,choices=USUARIO)
    administrador = models.BooleanField(default=False)
    sexo          = models.CharField(max_length=1,choices=SEXO)
    tlf_cel       = models.CharField(max_length=11) 	
    direccion     = models.CharField(max_length=128)
    tlf_casa      = models.CharField(max_length=11)
    habilitado    = models.BooleanField(default=False)

    def sexoR(self):
        resp = "Hombre"
        if (self.sexo == '2'):
            resp = "Mujer"
        return resp

    def tipoR(self):
        resp = "Administrador"
        if (self.tipo == '1'):
            resp = "Médico"
        if (self.tipo == '2'):
            resp = "Secretaria"
        if (self.tipo == '3'):
            resp = "Mujer"
        return resp
