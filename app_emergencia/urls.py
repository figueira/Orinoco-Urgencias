from django.conf.urls import patterns, url

from app_emergencia import views

urlpatterns = patterns(
    'app_emergencia.views',
    # Acesso a esperas
    url(
        '^emergencia/espera_mantener/(?P<id_emergencia>.*)$',
        'emergencia_espera_mantener'
    ),
    url(
        '^emergencia/(?P<id_emergencia>\d+)/agregar_espera/' +
        '(?P<id_espera>\d+)$',
        'emergencia_agregar_espera'
    ),
    url(
        '^emergencia/eliminar_espera_emergencia/(?P<id_espera_emergencia>.*)$',
        'emergencia_eliminar_espera_emergencia'
    ),
    url(
        '^emergencia/espera_estado/(?P<id_emergencia>.*)/' +
        '(?P<id_espera>.*)/(?P<espera>.*)$',
        'emergencia_espera_estado'
    ),
    url(
        '^emergencia/espera_finalizada/(?P<id_espera_emergencia>.*)$',
        'emergencia_espera_finalizada'
    ),
    url(
        '^emergencia/espera_asignadasCheck/(?P<id_emergencia>.*)$',
        'emergencia_espera_asignadasCheck'
    ),
    url(
        '^emergencia/espera_id/(?P<id_emergencia>.*)$',
        'emergencia_espera_id'
    ),
    url(
        '^emergencia/espera_idN/(?P<id_emergencia>.*)$',
        'emergencia_espera_idN'
    ),

    # Agregar emergencia de paciente existente
    url(
        '^emergencia/agrega_emer/(?P<id_emergencia>.*)$',
        'emergencia_agrega_emer'
    ),

    # Agregar/Modificar Cubiculo:
    url(
        '^emergencia/guardar_cubi/(?P<id_emergencia>.*)/(?P<accion>.*)$',
        'emergencia_guardar_cubi'
    ),
    url(
        '^emergencia/tiene_cubi/(?P<id_emergencia>.*)$',
        'emergencia_tiene_cubiculo'
    ),

    url('^emergencia/agregar$', 'emergencia_agregar'),
    url('^emergencia/listar/todas$',
        'emergencia_listar_todas'),
    url('^emergencia/listar/sinclasificar$',
        'emergencia_listar_sinclasificar'),
    url('^emergencia/listar/clasificados$',
        'emergencia_listar_clasificados'),
    url('^emergencia/listar/triage$',
        'emergencia_listar_triage'),
    url('^emergencia/listar/ambulatoria$',
        'emergencia_listar_ambulatoria'),
    url('^emergencia/listar/observacion$',
        'emergencia_listar_observacion'),
    url('^emergencia/listar/atencion$',
        'emergencia_listar_atencion'),
    url('^emergencia/buscarHistoria$',
        'emergencia_buscar_historia_medica'),
    url('^emergencia/(?P<idE>\d+)/aplicar_triage/(?P<vTriage>\d*)$',
        'emergencia_aplicarTriage'),
    url('^emergencia/(?P<idE>\d+)/triage/calcular/(?P<triage_asignado>\d*)$',
        'emergencia_calcular_triage'),
    url('^emergencia/(?P<idE>\d+)/daralta$',
        'emergencia_darAlta'),
    url('^emergencia/buscar$',
        'emergencia_buscar'),
    url('^emergencia/(?P<idE>\w+)/perfil$',
        'paciente_perfil_emergencia'),
)
