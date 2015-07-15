from django.conf.urls import patterns, include, url
from AM import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
# APLICACIONES PROPIAS
# Atencion
# Atencion

urlpatterns = patterns(
    '',
    # Emergencias
    url(r'^', include('app_emergencia.urls')),
    url(r'^', include('app_historiaMedica.urls')),
    url(r'^', include('app_paciente.urls')),

    # Usuario
    url('^$', 'app_usuario.views.sesion_iniciar'),
    url('^sesion/iniciar/$', 'app_usuario.views.sesion_iniciar'),
    url('^sesion/cerrar$', 'app_usuario.views.sesion_cerrar'),
    url('^usuario/solicitar$', 'app_usuario.views.usuario_solicitar'),
    url('^usuario/pendientes$', 'app_usuario.views.usario_listarPendientes'),
    url('^usuario/listar$', 'app_usuario.views.usario_listar'),
    url('^usuario/pendientes/(?P<cedulaU>\d+)/aprobar$',
        'app_usuario.views.usuario_aprobar'),
    url('^usuario/pendientes/(?P<cedulaU>\d+)/aprobarAdmin$',
        'app_usuario.views.usuario_aprobarAdmin'),
    url('^usuario/pendientes/(?P<cedulaU>\d+)/rechazar$',
        'app_usuario.views.usuario_rechazar'),
    url('^usuario/pendientes/(?P<cedulaU>\d+)/examinar$',
        'app_usuario.views.pendiente_examinar'),
    url('^usuario/clave$', 'app_usuario.views.clave_cambiar'),
    url('^usuario/restablecer$', 'app_usuario.views.clave_restablecer'),
    url('^usuario/crear$', 'app_usuario.views.usuario_crear'),
    url('^usuario/listar/(?P<cedulaU>\d+)/habilitar$',
        'app_usuario.views.usuario_habilitar'),
    url('^usuario/listar/(?P<cedulaU>\d+)/deshabilitar$',
        'app_usuario.views.usuario_deshabilitar'),
    url('^usuario/listar/(?P<cedulaU>\d+)/examinar$',
        'app_usuario.views.usuario_examinar'),
    url('^usuario/activar/(?P<cedulaU>\d+)/',
        'app_usuario.views.usuario_activar'),
    url('^usuario/desactivar/(?P<cedulaU>\d+)/',
        'app_usuario.views.usuario_desactivar'),
    url('^usuario/promover/(?P<cedulaU>\d+)/',
        'app_usuario.views.usuario_promover'),
    url('^usuario/despromover/(?P<cedulaU>\d+)/',
        'app_usuario.views.usuario_despromover'),

    # Estadisticas
    url('^estadisticas/$', 'app_emergencia.views.estadisticas'),
    url('^estadisticas/(?P<dia>\d+)-(?P<mes>\d+)-(?P<anho>\d+)$',
        'app_emergencia.views.estadisticas_sem'),
    url('^estadisticas/(?P<dia>\d+)-(?P<mes>\d+)-' +
        '(?P<anho>\d+)/(?P<dia2>\d+)-(?P<mes2>\d+)-(?P<anho2>\d+)$',
        'app_emergencia.views.estadisticas_per'),

    # Admin
    url(r'^admin/', include(admin.site.urls)),
    # Media
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
    # Static
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),

)
