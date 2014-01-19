/* 
  Hace que una serie de causas de espera se mantengan activas
  Entrada:
    El objeto de jQuery correspondiente a la fila en la que la espera se 
    imprime
*/
function MantenerEsperas(fila_emergencia){
  var id_emergencia = fila_emergencia.data('id-emergencia');
  fila_emergencia.data("tiempoesp", 0);
  fila_emergencia.data("tiempo_espera_inicio","0");
  fila_emergencia.css("background","white");
  $.get("/emergencia/espera_mantener/" + id_emergencia);
}

// Funcion que modifica cada segundo los tiempos de espera
function myTimer() {
  {% for emergencia in emergencias %}
    // Se toma el contenido actual del tiempo de espera
    var tiempo = $("#tiempo_{{ emergencia.id }}").text()
                                                 .split(":");
    dias = parseInt(tiempo[0]);
    horas = parseInt(tiempo[1]);
    minutos = parseInt(tiempo[2]);
    segundos = parseInt(tiempo[3]);

    var minutos_en_emergencia = (dias * 24 * 60) + (horas * 60) + minutos;

    // Se incrementa un segundo
    segundos += 1;

    if (segundos == 60) {
      segundos = 0;
      minutos = minutos + 1;
      if (minutos == 60) {
        minutos = 0;
        horas = horas + 1;
        if (horas == 24) {
          horas = 0;
          dias = dias + 1;
        }
      }
    }

    // Se colocan los 0 iniciales
    if (segundos < 10) segundos = "0" + segundos;
    if (minutos < 10) minutos = "0" + minutos;
    if (horas < 10) horas = "0" + horas;
    if (dias < 10) dias = "0" + dias;

    // Se reimprime el contador
    nuevo_tiempo = dias + ":" + horas + ":" + minutos + ":" + segundos;
    $("#tiempo_{{ emergencia.id }}").text(nuevo_tiempo);

    // Se determina el color del contador
    inicio_negro = 360; // 6 horas (360 minutos)
    inicio_rojo = 240; // 4 horas (240 minutos)
    inicio_amarillo = 120; // 2 horas (120 minutos)

    if (minutos_en_emergencia > inicio_negro) {
      $("#barra_{{emergencia.id}}").attr("class","bar bar-inverse");
    } else if (minutos_en_emergencia > inicio_rojo) {
      $("#barra_{{emergencia.id}}").attr("class","bar bar-danger");
    } else if (minutos_en_emergencia > inicio_amarillo) {
      $("#barra_{{emergencia.id}}").attr("class","bar bar-warning");
    }else{
      $("#barra_{{emergencia.id}}").attr("class","bar bar-success");
    }

    // Ahora se calcula cuanto tiempo lleva el paciente esperando
    tiempo_espera = +($("#emergencia_{{ emergencia.id }}")
                        .data("tiempoesp"));

    // Si el paciente lleva mas de media hora esperando, cambiar el fondo
    // de la celda
    if (tiempo_espera > 1800){
      $('#emergencia_{{emergencia.id}}')
        .css("background","rgba(230, 230, 230, 0.5)");
    } else {
      // Se modifica el atributo en el DOM solo cuando es necesario
      tiempo_espera = tiempo_espera + 1
      $("#emergencia_{{ emergencia.id }}").data("tiempoesp", 
                                                tiempo_espera);
    }

  {% endfor %}
}

function enviaA(emercy){
  $(function() {
    $('#'+emercy+'cub').change(function() {
      this.form.submit();
    });
  });
}

{% if user.is_authenticated %}

  function actualizar(emer){
    $(function() {
      $('#formCubA_'+emer).show();
      $('#cubDir_'+emer).replaceWith($('#formCubA_'+emer));
    });
  }

{% endif %}

function manito(emer){
/*        $(function() {
    $(this).hover("cursor", "hand");
  });*/
}

// Mueve la causa de espera asignada a la lista correspondiente de causas
// no asignadas
function mover_a_no_asignada(espera_asignada){
  var id_espera = espera_asignada.data('id-espera');
  var no_asignadas = espera_asignada.closest('.tabla-esperas')
                                    .find('.esperas-no-asignadas')
                                    .first();
  var item_lista = $('<li></li>');
  item_lista.addClass('espera-no-asignada');
  item_lista.attr('data-id-espera', id_espera);
  no_asignadas.append(item_lista);
  
  // Colocar el logo para eliminar la causa
  var menos = $('<img> </img>');
  menos.attr('src', '/static/img/Atencion/masim.png');
  menos.addClass('espera-mas');
  item_lista.append(menos);

  // Colocar la imagen de la causa de espera
  var imagen_espera = espera_asignada.children('.imagen-espera-lista')
                                     .first();
  item_lista.append(imagen_espera);

  // Colocar la causa de espera
  item_lista.append(espera_asignada.text());

  // Eliminar la imagen de la causa de espera del td
  imagen_td = espera_asignada.closest('.causas-espera')
                             .siblings('.imagenes-causas-espera')
                             .children('[data-id-espera=' + 
                                       id_espera + ']')
                             .first();
  imagen_td.remove();

  // Eliminar el elemento
  espera_asignada.remove()
}

// Acciones a realizar cuando la lista se termine de cargar
$(document).ready(function(){
  // Se empieza la funcion que actualiza los contadores
  var intervalo_tiempo = setInterval(function(){ myTimer() }, 1000);

  // Se inicializan contadores de filas
  var cont = 1;
  {% for emergencia in emergencias %}
    $("#emergencia_{{emergencia.id}}").data("fila",cont);
    $("#emergencia_{{emergencia.id}}").data("flat","0");
    cont++;
  {% endfor %}

  // Evento que oculta el panel de causas de espera cuando se hace click
  // fuera de el
  $(document.body).click(function(){
    $('.causas-espera').fadeOut();
  })

  // Asociacion del evento click al boton de mantener un grupo  de causas
  // de espera
  $('.boton-mantener').click(function(event){
    event.preventDefault();

    MantenerEsperas($($(this).closest('.fila-emergencia')))
  })

  // Asociacion del evento click sobre las esperas
  $('.boton-espera').click(function(event){
    event.preventDefault();
    event.stopPropagation();
    var causas_espera = $(this).children('.causas-espera');
    // Decidir que hacer dependiendo de si el panel con las causas de
    // espera esta visible o no
    if(causas_espera.css('display') == 'none')
    {
      $('.causas-espera').fadeOut();
      causas_espera.fadeIn();
    } else
    {
      $('.causas-espera').fadeOut();
    }
  });

  // Esto es para prevenir que el click en el panel de causas de espera
  // haga que el mismo desaparezca
  $('.causas-espera').click(function(event){
    event.stopPropagation();
  })

  // Método que agrega causas de espera a partir de la lista de causas
  // no asignadas
  $('.causas-espera').on('click', '.espera-mas', function(event){
    // Construir el elemento a agregar a la lista de causas asignadas
    var mas_activado = $(this);
    var id_espera = mas_activado.parent().data('id-espera');
    var fila_emergencia = $(mas_activado.closest('.fila-emergencia'));
    var id_emergencia = fila_emergencia.data('id-emergencia');
    
    // Antes que todo se envia una actualizacion a la base de datos para
    // guardar este cambio
    $.getJSON('/emergencia/' + id_emergencia + '/agregar_espera/' + 
              id_espera, '', function(id_retorno){
      var asignadas = mas_activado.closest('.tabla-esperas')
                                   .find('.esperas-asignadas')
                                   .first();
      var item_lista = $('<li></li>');
      item_lista.addClass('espera-asignada');
      item_lista.attr('data-id-espera', id_espera);
      item_lista.attr('data-id-espera-emergencia', id_retorno);
      asignadas.append(item_lista);
      
      // Colocar el logo para eliminar la causa
      var menos = $('<img> </img>');
      menos.attr('src', '/static/img/Atencion/menosim.png');
      menos.addClass('espera-menos');
      item_lista.append(menos);

      // Colocar el checkbox para marcar la causa como atendida
      var checkbox = $('<input></input>');
      checkbox.attr('type', 'checkbox');
      checkbox.addClass('espera-atendida');
      item_lista.append(checkbox);

      // Colocar la imagen de la causa de espera
      var imagen_espera = mas_activado.siblings('.imagen-espera-lista')
                                      .first();
      item_lista.append(imagen_espera.clone());

      // Colocar la causa de espera
      item_lista.append(mas_activado.parent().text());

      // Agregar la imagen de la causa de espera al td adyacente
      imagen_espera.removeClass('imagen-espera-lista');
      imagen_espera.addClass('imagen-espera-td');
      mas_activado.closest('.causas-espera')
                  .siblings('.imagenes-causas-espera')
                  .append(imagen_espera);

      // Eliminar el elemento
      mas_activado.parent().remove();

      // Finalmente indicar que se mantengan las causas de espera
      MantenerEsperas(fila_emergencia)
    });
  });

  // Método que elimina causas de espera a partir de la lista de causas
  // asignadas
  $('.causas-espera').on('click', '.espera-menos', function(event){
    var menos_activado = $(this)
      if(confirm('¿Esta seguro que desea eliminar "' + 
                 $.trim(menos_activado.parent().text()) + '"? ' +
                 "Esto no la marcará como cumplida, para ello use la " +
                 "caja adyacente"))
      {
      // Construir el elemento a agregar a la lista de causas no asignadas
      var id_espera_emergencia = menos_activado.parent()
                                               .data('id-espera-emergencia');
      var id_emergencia = menos_activado.closest('.fila-emergencia')
                                        .data('id-emergencia');

      // Hacer peticion a la base de datos para eliminar la causa de espera
      $.get('/emergencia/eliminar_espera_emergencia/' + 
            id_espera_emergencia, function(){
        mover_a_no_asignada(menos_activado.parent())
      });
    }
  });

  // Asociacion del evento sobre el checkbox que marca una causa de espera
  // como finalizada
  $('.esperas-asignadas').on('click', '.espera-atendida', function(){
    var checkbox_activado = $(this);
    if(confirm('¿Está seguro que desea marcar "' +
                $.trim(checkbox_activado.parent().text()) + 
                '" como cumplida? Esta acción no es reversible')){
      var id_espera_emergencia = checkbox_activado
                                 .parent()
                                 .data('id-espera-emergencia');

      // Hacer peticion a la base de datos para finalizar la espera
      $.get('/emergencia/espera_finalizada/' + id_espera_emergencia, 
            function(){
        mover_a_no_asignada(checkbox_activado.parent())
      });
    } else {
      checkbox_activado.prop('checked', false)
    }
  });

  // Especialmente para Firefox, se deben asignar las propiedades
  // correctas a los checkbox y los option
  $('.espera-atendida').each(function(){
    checkbox = $(this)
    if(checkbox.attr('checked') == 'checked'){
      checkbox.prop('checked', 'checked')
    } else {
      checkbox.removeProp('checked')
    }
  });

  $('option').each(function(){
    option = $(this);
    if(option.attr('selected') == 'selected'){
      option.prop('selected', 'selected')
    }else{
      option.removeProp('selected')
    }
  })

  $(".formCubA").css("display","none");
  $("[rel='tooltip']").tooltip();
  $(".tit-list").html("{{titulo}}")
});
