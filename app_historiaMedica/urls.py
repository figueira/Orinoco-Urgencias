from django.conf.urls import patterns, url

from app_emergencia import views as emergencia_View
from app_historiaMedica import views as historiaM_Views

urlpatterns = patterns(
    '',
    # Acceso a Atencion
    url(
        '^emergencia/atencion/(?P<id_emergencia>.*)/(?P<tipo>.*)$',
        historiaM_Views.emergencia_atencion
    ),
    url(
        '^emergencia/(?P<idE>\d+)/actualizarSig$',
        emergencia_View.actualizarSignos
    ),
    # Acceso a Enfermedad Actual
    url(
        '^emergencia/enf_actual/(?P<id_emergencia>.*)$',
        historiaM_Views.emergencia_enfermedad_actual
    ),
    # Acciones Antecedentes
    url(
        '^emergencia/antecedentes/(?P<id_emergencia>.*)/' +
        '(?P<tipo_ant>.*)/agregar$',
        historiaM_Views.emergencia_antecedentes_agregar
    ),
    url(
        '^emergencia/antecedentes/(?P<id_emergencia>.*)/' +
        '(?P<tipo_ant>.*)/modificar$',
        historiaM_Views.emergencia_antecedentes_modificar
    ),
    url(
        '^emergencia/antecedentes/(?P<id_emergencia>.*)/' +
        '(?P<tipo_ant>.*)/eliminar$',
        historiaM_Views.emergencia_antecedentes_eliminar
    ),

    # Ingreso a antecedentes
    url(
        '^emergencia/antecedentes/(?P<id_emergencia>.*)/' +
        '(?P<tipo_ant>.*)$',
        historiaM_Views.emergencia_antecedentes_tipo
    ),
    url(
        '^emergencia/antecedente/(?P<id_emergencia>.*)$',
        historiaM_Views.emergencia_antecedentes
    ),

    # Ingreso a Examen fisico
    url(
        '^emergencia/enviarcuerpo/(?P<id_emergencia>.*)/(?P<parte_cuerpo>.*)$',
        historiaM_Views.emergencia_enfermedad_enviarcuerpo
    ),
    url(
        '^emergencia/partecuerpo/(?P<id_emergencia>.*)/(?P<parte_cuerpo>.*)$',
        historiaM_Views.emergencia_enfermedad_partecuerpo
    ),
    url(
        '^emergencia/cuerpo/(?P<id_emergencia>.*)/(?P<zona_cuerpo>.*)$',
        historiaM_Views.emergencia_enfermedad_zonacuerpo
    ),
    url(
        '^emergencia/enfermedad/(?P<id_emergencia>.*)$',
        historiaM_Views.emergencia_enfermedad
    ),

    # Ingreso a Indicaciones
    # Acciones:
    # Listar detalles indicacion:
    url(
        '^emergencia/infoInd/(?P<id_asignacion>.*)/(?P<tipo_ind>.*)$',
        historiaM_Views.emergencia_indicacion_info
    ),
    # Agregar
    url(
        '^emergencia/indicaciones/(?P<id_emergencia>.*)/' +
        '(?P<tipo_ind>.*)/agregar$',
        historiaM_Views.emergencia_indicaciones_agregar
    ),
    # Eliminar
    url(
        '^emergencia/indicaciones/(?P<id_emergencia>.*)/' +
        '(?P<tipo_ind>.*)/eliminar$',
        historiaM_Views.emergencia_indicaciones_eliminar
    ),
    # Modificar
    url(
        '^emergencia/indicaciones/(?P<id_emergencia>.*)/' +
        '(?P<tipo_ind>.*)/modificar$',
        historiaM_Views.emergencia_indicaciones_modificar
    ),

    # Ingreso a Indicaciones Especializadas
    url(
        '^emergencia/indicaciones/(?P<id_emergencia>.*)/(?P<tipo_ind>.*)$',
        historiaM_Views.emergencia_indicaciones
    ),

    # Ingreso a Indicaciones general
    url(
        '^emergencia/indi/(?P<id_emergencia>.*)$',
        historiaM_Views.emergencia_indicaciones_ini
    ),

    # -------------------------------------------fIND

    # Ingreso a Diagnostico Definitivo
    url(
        '^emergencia/diagnostico/(?P<id_emergencia>.*)$',
        historiaM_Views.emergencia_diagnostico
        ),

    # Botones genericos de atencion:
    # Descargar de pdfs:
    url(
        '^emergencia/descarga/(?P<id_emergencia>.*)/(?P<tipo_doc>.*)$',
        historiaM_Views.emergencia_descarga
    ),

    # Realizar la evaluacion de un paciente asociado a una emergencia
    url(
        '^emergencia/(?P<id_emergencia>\d+)/evaluar_paciente$',
        historiaM_Views.evaluar_paciente
    ),
)
