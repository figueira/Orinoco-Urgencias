/*
  Realiza la respuesta a la petición de hacer realizar la evaluacion de un
  paciente.

  Entrada:
    form -> El formulario que fue dado
 */
{% if es_valido %}
  console.log('Valido!');
{% else %}
  $('.formulario-evaluacion').replaceWith("{{ plantilla_formulario | escapejs }}")
{% endif %}
