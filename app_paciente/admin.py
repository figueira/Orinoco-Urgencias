from app_paciente.models import *
from django.contrib import admin

admin.site.register(Paciente)
admin.site.register(Antecedente)
admin.site.register(Pertenencia)
admin.site.register(Lugar)
admin.site.register(LugarPertenencia)
admin.site.register(Tratamiento)
admin.site.register(TratamientoPertenencia)
admin.site.register(Fecha)
