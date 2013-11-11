function MantenerEsperas(emer){
  $("#emergencia_"+emer).data("tiempoEsp","0:0:0:0");
  $("#emergencia_"+emer).data("tiempo_espera_inicio","0");
  $('#emergencia_'+emer).css("background","white");
  //emergencia/espera_mantener/(?P<id_emergencia>.*)
  $.get("/emergencia/espera_mantener/"+emer);
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
  
  $("#emergencia_"+emer).data("tiempoEsp","0:0:0:0");
  $("#emergencia_"+emer).data("tiempo_espera_inicio","0");
  $('#emergencia_'+emer).css("background","white");

  $('#texto'+emer).attr("texto",num);
  $('#texto'+emer).html(""+num+""); 
  $.get("/emergencia/espera_estado/"+emer+"/"+i+"/"+estado);
}

function eliminar(emer,i){
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
  $.get("/emergencia/espera_eliminar/" + emer + "/" + i);

  // Eliminar la imagen de la lista
  $("#emergencia_" + emer).data("tiempoEsp","0:0:0:0");
  $("#emergencia_" + emer).data("tiempo_espera_inicio","0");
  $('#emergencia_' + emer).css("background","white");

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
  $("#emergencia_" + emer).data("tiempoEsp","0:0:0:0");
  $("#emergencia_" + emer).data("tiempo_espera_inicio","0");
  $('#emergencia_' + emer).css("background","white");
}

function modificar(emer){
  var contenido = "";
  var imagenIni = '<img id="img_' + emer + '-';
  var imagenFin = '" style="width:22px;height:22px;" ' + 
                  'src="/static/img/esperas/espera_';
  var finImagen = '.png"/>';
  var menos     = '<img src="/static/img/Atencion/menosim.png" ' +
                  'class="imagenIcono" title="-" onClick="eliminar(' + emer + 
                  ',';
  var mas       = '<img src="/static/img/Atencion/masim.png" class="imagenIcono"' +
                  'title="-" onClick="agregar('+emer+',';
  var checkbox  = '<input type="checkbox" onchange="estado(' + emer + ',';
  var check = ')" name="check" />';
  var checkbox2 = '<input type="checkbox" onchange="estado(' + emer + ',';
  var check2 = ')" name="check" checked />';

  // Eliminar las listas que esta construida actualmente
  $(".esperaC_"+emer).each(function(index,valor){
    $(valor).remove();
  });
    
  $.getJSON("/emergencia/espera_asignadas/" + emer, function(esperasAsignadas){
    $.getJSON("/emergencia/espera_noAsignadas/" + emer, function(esperasNoAsignadas){
      // Construir la seccion de esperas asignadas
      $.each(esperasAsignadas, function(i, espera){
        // Revisar si el elemento esta marcado como atendido
        if (espera.estado  == "0")
        {
          contenido = contenido + '<li id="' + emer + '-' + espera.id + i +
                      '"><span>' + menos + espera.id + ')"/></span>' +
                      checkbox + espera.id + check + imagenIni + espera.id +
                      imagenFin + espera.id + finImagen + " " + espera.nombre +
                      "</li>";
          $('#causas_' + emer).before(
            '<img id="img_' + emer + '_' + espera.id + 
            '" style="width:50px;height:50px;" class = "esperaC_' + emer + 
            '" src="/static/img/esperas/espera_' + espera.id + '.png"/>');
        }else if(espera.estado == "1")
        {
          contenido = contenido + '<li id="' + emer + '-' + espera.id + 
                      '">' + '<span>' + menos + espera.id + ')"/>' + 
                      '</span>' + checkbox2 + espera.id + check2 + 
                      imagenIni + espera.id + imagenFin + espera.id + 
                      finImagen + " " + espera.nombre + "</li>";
        }
      });

      contenido = contenido + '<hr id="hr' + emer + '">';

      // Construir la seccion de esperas no asignadas
      $.each(esperasNoAsignadas, function(i, espera){
        contenido = contenido + '<li id="' + emer + '-' + espera.id + 
                    '">' + '<span>' + mas + espera.id + ')"/>' + 
                    '</span>' + imagenIni + espera.id + imagenFin + 
                    espera.id + finImagen + " " + espera.nombre + "</li>";
      });

      // Asignar el contenido construido al elemento apropiado
      $("#espera"+emer).attr('data-content',contenido);
    });
  });
}

function contenido(emer){
  modificar(emer);
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
