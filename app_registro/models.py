from django.db import models
from app_usuario.models import *

# Create your models here.
class Registro(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario)
    accion  = models.CharField(max_length=512)
