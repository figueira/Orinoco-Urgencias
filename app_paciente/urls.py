from django.conf.urls import patterns, url


from app_paciente import views
from app_perfil import  views as perfil_views

urlpatterns = patterns(
    '',
    # Paciente
    url(
        '^paciente/eliminarEnfermedad/' +
        '(?P<codigo_enfermedad>\w*)/(?P<codigo_paciente>\w*)$',
        views.eliminarEnfermedad
    ),
    url(
        '^paciente/agregarEnfermedad/(?P<codigo_enfermedad>\w*)/' +
        '(?P<codigo_paciente>\w*)$',
        views.agregarEnfermedad
    ),
    url(
        '^paciente/buscarEnfermedad/(?P<nombre_enfermedad>.*)$',
        views.buscarEnfermedad
    ),
    url('^paciente/listarPacientes$',
        views.paciente_listarPacientes),
    url('^paciente/buscarjson/(?P<ced>\w+)$',
        views.buscarPacienteJson),
    url('^paciente/(?P<idP>\w+)$',
        views.paciente_perfil),
    url(
        '^paciente/(?P<idP>\w+)/triage$',
        perfil_views.reporte_triage
    ),
    url(
        '^paciente/(?P<idP>\w+)/editar$',
        views.editarPaciente
    ),
    url('^paciente/(?P<idP>\d+)/emergencias$',
        views.ver_emergencias),
)
