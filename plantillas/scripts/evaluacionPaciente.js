/*
  Realiza la respuesta a la petición de hacer realizar la evaluacion de un
  paciente.

  Entrada:
    form -> El formulario que fue dado
 */
$('.formulario-evaluacion').replaceWith("{{ plantilla_formulario | escapejs }}")
{% if es_valido %}
  $('.tab-triage').fadeOut();
  $('#litab1').fadeIn();
{% else %}
  $('.tab-triage').fadeOut();
{% endif %}
