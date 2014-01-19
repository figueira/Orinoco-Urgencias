/*
  Realiza la respuesta a la petición de hacer realizar la evaluacion de un
  paciente.

  Entrada:
    es_valido -> Booleano indicando si el formulario dado es valido
    id_emergencia -> El identificador de la emergencia en cuestion
    plantilla_formulario -> El formulario que fue dado
 */

$('.formulario-evaluacion').replaceWith("{{ plantilla_formulario | escapejs }}")
{% if es_valido %}
  triage_asignado = $('.triage-asignado').text();
  if(triage_asignado == ''){
    // Si no se asigno previamente ningun triage, mostrar la primera pregunta
    $('.tab-triage').fadeOut();
    $('#litab1').fadeIn();
    $('a[href = #tab1]').click();

    // Se debe inicializar el datepicker
    $('#ingreso_picker').datetimepicker({
      language: 'pt-BR'
    });
  } else {
    // De lo contrario, se asigna inmediatamente el triage
    url_triage = '/emergencia/{{ id_emergencia }}/aplicar_triage/' +
                 triage_asignado;
    window.location.replace(url_triage)
  }
{% else %}
  $('.tab-triage').fadeOut();
{% endif %}
