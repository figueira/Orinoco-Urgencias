from django.conf.urls import patterns, include, url
from AM import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    ## APLICACIONES PROPIAS
    # Atencion
  	# Atencion
    url(r'^', include('app_emergencia.urls')),
  
    # Usuario
    url('^$','app_usuario.views.sesion_iniciar'),
    url('^sesion/iniciar/$','app_usuario.views.sesion_iniciar'),
    url('^sesion/cerrar$','app_usuario.views.sesion_cerrar'),
    url('^usuario/solicitar$','app_usuario.views.usuario_solicitar'),
    url('^usuario/pendientes$','app_usuario.views.usario_listarPendientes'),
    url('^usuario/listar$','app_usuario.views.usario_listar'),
    url('^usuario/pendientes/(?P<cedulaU>\d+)/aprobar$',
        'app_usuario.views.usuario_aprobar'),
    url('^usuario/pendientes/(?P<cedulaU>\d+)/rechazar$',
        'app_usuario.views.usuario_rechazar'),
    url('^usuario/pendientes/(?P<cedulaU>\d+)/examinar$',
        'app_usuario.views.pendiente_examinar'),
    url('^usuario/clave$','app_usuario.views.clave_cambiar'),
    url('^usuario/restablecer$','app_usuario.views.clave_restablecer'),
    url('^usuario/crear$','app_usuario.views.usuario_crear'),
    url('^usuario/listar/(?P<cedulaU>\d+)/habilitar$',
        'app_usuario.views.usuario_habilitar'),
    url('^usuario/listar/(?P<cedulaU>\d+)/deshabilitar$',
        'app_usuario.views.usuario_deshabilitar'),
    url('^usuario/listar/(?P<cedulaU>\d+)/examinar$',
        'app_usuario.views.usuario_examinar'),

    # Emergencias
    url('^emergencia/agregar$','app_emergencia.views.emergencia_agregar'),
    url('^emergencia/listar/todas$',
        'app_emergencia.views.emergencia_listar_todas'),
    url('^emergencia/listar/sinclasificar$',
        'app_emergencia.views.emergencia_listar_sinclasificar'),
    url('^emergencia/listar/clasificados$',
        'app_emergencia.views.emergencia_listar_clasificados'),
    url('^emergencia/listar/triage$',
        'app_emergencia.views.emergencia_listar_triage'),
    url('^emergencia/listar/ambulatoria$',
        'app_emergencia.views.emergencia_listar_ambulatoria'),
    url('^emergencia/listar/observacion$',
        'app_emergencia.views.emergencia_listar_observacion'),
    url('^emergencia/listar/atencion/(?P<mensaje>.*)$',
        'app_emergencia.views.emergencia_listar_atencion'),
    url('^emergencia/(?P<idE>\d+)/aplicar_triage/(?P<vTriage>\d*)$',
        'app_emergencia.views.emergencia_aplicarTriage'),
    url('^emergencia/(?P<idE>\d+)/triage/calcular/(?P<triage_asignado>\d*)$',
        'app_emergencia.views.emergencia_calcular_triage'),
    url('^emergencia/(?P<idE>\d+)/daralta$',
        'app_emergencia.views.emergencia_darAlta'),   
    url('^emergencia/buscar$','app_emergencia.views.emergencia_buscar'),   

    # Estadisticas
    url('^estadisticas/$','app_emergencia.views.estadisticas'),
    url('^estadisticas/(?P<dia>\d+)-(?P<mes>\d+)-(?P<anho>\d+)$',
        'app_emergencia.views.estadisticas_sem'),
    url('^estadisticas/(?P<dia>\d+)-(?P<mes>\d+)-(?P<anho>\d+)/(?P<dia2>\d+)-(?P<mes2>\d+)-(?P<anho2>\d+)$',
        'app_emergencia.views.estadisticas_per'),

    # Paciente
    url('^paciente/eliminarEnfermedad/(?P<codigo_enfermedad>\w*)/(?P<codigo_paciente>\w*)$',
        'app_paciente.views.eliminarEnfermedad'),
    url('^paciente/agregarEnfermedad/(?P<codigo_enfermedad>\w*)/(?P<codigo_paciente>\w*)$',
        'app_paciente.views.agregarEnfermedad'),
    url('^paciente/buscarEnfermedad/(?P<nombre_enfermedad>.*)$',
        'app_paciente.views.buscarEnfermedad'),
    url('^paciente/listarPacientes$',
        'app_paciente.views.paciente_listarPacientes'),
    url('^paciente/buscarjson/(?P<ced>\w+)$',
        'app_paciente.views.buscarPacienteJson'),                           
    url('^paciente/(?P<idP>\w+)$',
        'app_perfil.views.paciente_perfil'),
    url('^paciente/(?P<idP>\w+)/triage$','app_perfil.views.reporte_triage'),

    ## COSAS DJANGISTICAS
    # Admin
    url(r'^admin/', include(admin.site.urls)),
    # Media
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
    # Static
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.STATIC_ROOT}),


    # Examples:
    # url(r'^$', 'AM.views.home', name='home'),
    # url(r'^AM/', include('AM.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
