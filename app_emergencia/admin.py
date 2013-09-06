from app_emergencia.models import *
from django.contrib import admin

admin.site.register(Emergencia)
admin.site.register(Triage)
admin.site.register(Motivo)
admin.site.register(AreaEmergencia)
admin.site.register(AreaAdmision)
admin.site.register(Cubiculo)
admin.site.register(Destino)
admin.site.register(AsignarCub)

#--Esperas
admin.site.register(Espera)
admin.site.register(EsperaEmergencia)

#--Fases Atencion
admin.site.register(Atencion)
admin.site.register(EnfermedadActual)
admin.site.register(Indicacion)
admin.site.register(Asignar)
admin.site.register(EspDieta)
admin.site.register(EspHidrata)
admin.site.register(CombinarHidrata)
admin.site.register(EspMedics)
admin.site.register(EspImg)
admin.site.register(tieneSOS)

#--Diagnostico
admin.site.register(Diagnostico)
admin.site.register(EstablecerDiag)