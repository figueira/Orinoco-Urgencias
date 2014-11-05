// Funcion que responde al exito de la llamada a ajax para hacer la
// evaluacion de fecha
$(document).ready(function(){
  $('#ingreso_picker').datetimepicker({
    language: 'pt-BR'
  });

  // Se pide la submision del formulario de manera asincrona
  $('.tab-evaluacion').on('click',
                          '.boton-evaluar',
                          function(event){
    var formulario = $('.formulario-evaluacion');
    event.preventDefault();
    $.ajax({
            data: formulario.serialize(),
            dataType: 'script',
            type: formulario.attr('method'),
            url: formulario.attr('action')
           })
  })

  // Evento sobre respuesta negativa en la primera pregunta
  $("#no_inmediata").click(function() {
    $('#litab2').fadeIn();
    $('a[href = #tab2]').click();
    $('#litab3').fadeOut();
  });

  $("#si_espera").click(function() {
    $('#litab3').fadeIn();
    $('a[href = #tab3]').click();
  });

  $("#ahora").click(function() {
    var currentTime = new Date()
    var mes = currentTime.getMonth() + 1;
    var dia = currentTime.getDate();
    var ano = currentTime.getFullYear();
    
    var horas    = currentTime.getHours()
    var minutos  = currentTime.getMinutes()
    var segundos = currentTime.getSeconds()
    $("#id_fecha").val(dia+"/"+mes+"/"+ano+" "+horas+":"+minutos+":"+segundos)
  });
})