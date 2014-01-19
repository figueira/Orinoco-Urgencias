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

function estado(emer,i)
{
  var estado="";
  var num = parseInt($('#texto' + emer).attr("texto"));
  
  if($("#" + emer + '-' + i).find('input').is(':checked')) 
  {
    num = num - 1;
    estado = "1";
    $('#img_' + emer + '_' + i).remove();
  } else 
  {
    num = num + 1;
    estado = "0";
    $('img_' + emer + '_' + i).remove();

    // Construir la imagen que sera agregada si la caja es desmarcada
    var imagenEspera = $("<img></img>");
    imagenEspera.attr("id", "img_" + emer + "_" + i);
    imagenEspera.attr("src", "/static/img/esperas/espera_" + i + ".png")
    imagenEspera.css("width", "50px");
    imagenEspera.css("height", "50px");
    imagenEspera.addClass("esperaC_" + emer);
    
    $('#causas_' + emer).after(imagenEspera)
  }
  
  $("#emergencia_"+emer).data("tiempoesp","0:0:0:0");
  $("#emergencia_"+emer).data("tiempo_espera_inicio","0");
  $('#emergencia_'+emer).css("background","white");

  $('#texto'+emer).attr("texto",num);
  $('#texto'+emer).html(""+num+""); 
  $.get("/emergencia/espera_estado/"+emer+"/"+i+"/"+estado);
}

function eliminar(emer,i){
  // Se hace la petición para eliminar la causa de espera
  $.get("/emergencia/espera_eliminar/" + emer + "/" + i, function(){
    // Habiendo recibido respuesta del servidor, se procede a cambiar el DOM

    // Eliminar la imagen de la lista
    $('#img_' + emer + '_' + i).remove();

    // Actualizar el contador de causas de espera
    var num = parseInt($('#texto' + emer).attr("texto"));
    if(!$("#" + emer + '-' + i).find('input').is(':checked')){
      console.log("Input no seleccionado");
      num = num - 1;
      $('#texto' + emer).attr("texto", num);
      $('#texto' + emer).html("" + num + "");
    }
    
    // Insertar el <li> seleccionado del lado inferior con el logo '+' y el
    // evento, y eliminar el checkbox
    $('#' + emer + '-' + i).insertAfter($('#hr' + emer));
    $('#' + emer + '-' + i).find('.imagenIcono').attr('src','/static/img/Atencion/masim.png');
    $('#' + emer + '-' + i).find('.imagenIcono').attr('onClick','agregar(' + emer + ',' + i + ')');
    $('#' + emer + '-' + i).find('input').remove();

    $("#emergencia_" + emer).data("tiempoesp","0:0:0:0");
    $("#emergencia_" + emer).data("tiempo_espera_inicio","0");
    $('#emergencia_' + emer).css("background","white");
  });
}

function agregar(emer,i){
  // Aumentar el contador de causas de espera
  var num = parseInt($('#texto'+emer).attr("texto"))+1;
  $('#texto'+emer).attr("texto",num);
  $('#texto'+emer).html(""+num+"");

  // Insertar el <li> seleccionado del lado superior con el logo de '-' y el
  // evento
  $('#'+emer+'-'+i).insertBefore($('#hr'+emer));
  $('#'+emer+'-'+i).find('.imagenIcono').attr('src','/static/img/Atencion/menosim.png');
  $('#'+emer+'-'+i).find('.imagenIcono').attr('onClick','eliminar('+emer+','+i+')');

  // Al <li> insertado se le coloca un checkbox
  $('#'+emer+'-'+i).find('input').show();
  $('#'+emer+'-'+i).find('span').after('<input type="checkbox" onchange="estado('+emer+','+i+')" name="check" value="{{i.antecedente.id}}" />');
  $.get("/emergencia/espera_agregar/"+emer+"/"+i);

  // Agregar la imagen grande en causas de espera
  $('img_' + emer + '_' + i).remove();
  $('#causas_' + emer).before('<img id="img_' + emer + '_' + i + 
                              '" class = "esperaC_' + emer + 
                              '" style="width:50px;height:50px;" ' +
                              'src="/static/img/esperas/espera_' + i + 
                              '.png"/>');
  $("#emergencia_" + emer).data("tiempoesp","0:0:0:0");
  $("#emergencia_" + emer).data("tiempo_espera_inicio","0");
  $('#emergencia_' + emer).css("background","white");
}

function mostrar_esperas(emer){
  var contenido = "";

  var menos = $('<img> </img>');
  menos.attr('src', '/static/img/Atencion/menosim.jpg');
  menos.addClass('imagenIcono');

  var mas = $('<img> </img>');
  menos.attr('src', '/static/img/Atencion/masim.jpg');
  menos.addClass('imagenIcono');

  // Eliminar las listas que esta construida actualmente
  $(".esperaC_"+emer).each(function(index,valor){
    $(valor).remove();
  });
    
  $.getJSON("/emergencia/espera_asignadas/" + emer, function(esperas_asignadas){
    $.getJSON("/emergencia/espera_noAsignadas/" + emer, function(esperas_no_asignadas){
      // Construir la seccion de esperas asignadas
      // Construir el elemento de la seccion de esperas asignadas
      var lista_esperas = $('<ul> </ul>');
      $.each(esperas_asignadas, function(i, espera){
        var list_item = $('<li> </li>');
        var checkbox = $('<input> </input>');
        var span_item = $('<span> </span>');
        var item_imagen_espera = $('<img> </img>');

        list_item.attr('id', emer + '-' + espera.id + i);

        checkbox.attr('type', 'checkbox')

        item_imagen_espera.attr('id', emer + '-' + espera.id);
        item_imagen_espera.attr('src', '/static/img/esperas/espera_' +
                                       espera.id +
                                       '.png');
        item_imagen_espera.css('width', '22px');
        item_imagen_espera.css('height', '22px');

        span_item.append(menos);
        list_item.append(span_item)

        // Revisar si el elemento esta marcado como atendido
        if (espera.estado  == "0")
        {
          ckeckbox.attr('checked', 'true');
          $('#causas_' + emer).before(
            '<img id="img_' + emer + '_' + espera.id + 
            '" style="width:50px;height:50px;" class = "esperaC_' + emer + 
            '" src="/static/img/esperas/espera_' + espera.id + '.png"/>');
        }else if(espera.estado == "1")
        {
          checkbox.attr('checked', 'false');
        }

        list_item.append(checkbox);
        list_item.append(item_imagen_espera);
        list_item.text(espera.nombre);

        lista_esperas.append(list_item);
      });

      $("#espera"+emer).append(lista_esperas);
      $("#espera"+emer).append($('<hr> </hr>'));
      
      // Construir la seccion de esperas no asignadas
      lista_no_esperas = $('<ul> </ul>')
      $("#espera"+emer).append(lista_no_esperas);
      $.each(esperas_no_asignadas, function(i, espera){
        var list_item = $('<li> </li>');
        var checkbox = $('<input> </input>');
        var span_item = $('<span> </span>');
        var item_imagen_espera = $('<img> </img>');

        lista_no_esperas.append(list_item);
        list_item.append(item_imagen_espera);
        list_item.append(span_item)
        span_item.append(mas);
        list_item.text(espera.nombre);

        list_item.attr('id', emer + '-' + espera.id + i);

        checkbox.attr('type', 'checkbox')

        item_imagen_espera.attr('id', emer + '-' + espera.id);
        item_imagen_espera.attr('src', '/static/img/esperas/espera_' +
                                       espera.id +
                                       '.png');
        item_imagen_espera.css('width', '22px');
        item_imagen_espera.css('height', '22px');


        console.log(list_item.html());
        console.log(span_item.html());
        console.log(item_imagen_espera.html());


      });
    });
  });
}

function contenido(emer){
  //modificar(emer);
}

$(document).ready(function () {
  $('.espera').popover('hide');
  
  $('.espera').each(function(index,valor){
    contenido($(this).attr('idEmer'));

    //modificar($(this).attr('idEmer'));
  });

  $('.espera').click(function(e){
    var emer    = $(this).attr('idEmer');
    var numFila = parseInt($("#emergencia_"+emer).data("fila")); 
    contenido(emer);
    if (numFila>3){$("body").animate({scrollTop:e.pageY -200},"300");}
  });
});
