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
    var reason_image = $("<img></img>");
    reason_image.attr("id", "img_" + emer + "_" + i);
    reason_image.attr("src", "/static/img/esperas/espera_" + i + ".png")
    reason_image.css("width", "50px");
    reason_image.css("height", "50px");
    reason_image.addClass("esperaC_" + emer);
    
    $('#causas_' + emer).after(reason_image)
  }
  
  $("#emergencia_"+emer).data("tiempoEsp","0:0:0:0");
  $("#emergencia_"+emer).data("tiempo_espera_inicio","0");
  $('#emergencia_'+emer).css("background","white");

  $('#texto'+emer).attr("texto",num);
  $('#texto'+emer).html(""+num+""); 
  $.get("/emergencia/espera_estado/"+emer+"/"+i+"/"+estado);
}

function eliminar(emer,i){
  var num = parseInt($('#texto'+emer).attr("texto"));
  if(!$("#"+emer+'-'+i).find('input').is(':checked')){
    num = num-1;
    $('#texto'+emer).attr("texto",num);
    $('#texto'+emer).html(""+num+"");
  }
  
  $('#'+emer+'-'+i).insertAfter($('#hr'+emer));
  $('#'+emer+'-'+i).find('.imagenIcono').attr('src','/static/img/Atencion/masim.png');
  $('#'+emer+'-'+i).find('.imagenIcono').attr('onClick','agregar('+emer+','+i+')');
  $('#'+emer+'-'+i).find('input').remove();
  $.get("/emergencia/espera_eliminar/"+emer+"/"+i);

  $('#img_'+emer+'_'+i).remove();
  $("#emergencia_"+emer).data("tiempoEsp","0:0:0:0");
  $("#emergencia_"+emer).data("tiempo_espera_inicio","0");
  $('#emergencia_'+emer).css("background","white");

}

function agregar(emer,i){
  var num = parseInt($('#texto'+emer).attr("texto"))+1;
  $('#texto'+emer).attr("texto",num);
  $('#texto'+emer).html(""+num+"");

  $('#'+emer+'-'+i).insertBefore($('#hr'+emer));
  $('#'+emer+'-'+i).find('.imagenIcono').attr('src','/static/img/Atencion/menosim.png');
  $('#'+emer+'-'+i).find('.imagenIcono').attr('onClick','eliminar('+emer+','+i+')');

  $('#'+emer+'-'+i).find('input').show();
  $('#'+emer+'-'+i).find('span').after('<input type="checkbox" onchange="estado('+emer+','+i+')" name="check" value="{{i.antecedente.id}}" />');
  $.get("/emergencia/espera_agregar/"+emer+"/"+i);

  $('img_'+emer+'_'+i).remove();
  $('#causas_'+emer).before('<img id="img_'+emer+'_'+i+'" class = "esperaC_'+emer+'" style="width:50px;height:50px;" src="/static/img/esperas/espera_'+i+'.png"/>');
  $("#emergencia_"+emer).data("tiempoEsp","0:0:0:0");
  $("#emergencia_"+emer).data("tiempo_espera_inicio","0");
  $('#emergencia_'+emer).css("background","white");
}

function modificar(emer){
  $.get("/emergencia/espera_asignadas/"+emer,function (data){
    $.get("/emergencia/espera_noAsignadas/"+emer,function (data2){
      $.get("/emergencia/espera_asignadasCheck/"+emer,function (data3){
        $.get("/emergencia/espera_id/"+emer,function (data4){
          $.get("/emergencia/espera_idN/"+emer,function (data5){
            var esperasAsig   = data.substring(0,data.length-1);
            if(esperasAsig ==""){esperasAsig = [];}
            else{esperasAsig  = esperasAsig.split(",");}
            
            var esperasNasig  = data2.substring(0,data2.length-1);
            if(esperasNasig ==""){esperasNasig = [];}
            else{esperasNasig  = esperasNasig.split(",");}
            
            var esperasChecki = data3.substring(0,data3.length-1);
            if(esperasChecki ==""){esperasChecki = [];}
            else{esperasChecki = esperasChecki.split(",");}

            var indexAsig     = data4.substring(0,data4.length-1);
            if(indexAsig ==""){indexAsig =[];}
            else{indexAsig  = indexAsig.split(",");}

            var indexNasig  = data5.substring(0,data5.length-1);
            if(indexNasig == "" ){indexNasig = [];}
            else{indexNasig = indexNasig.split(",");}

            var tamano1 = esperasAsig.length +esperasNasig.length;          
            var i = 0;
            var contenido = "";
            var imagenIni = '<img id="img_'+emer+'-';
            var imagenFin = '" style="width:22px;height:22px;" src="/static/img/esperas/espera_';
            var finImagen = '.png"/>';
            var menos     = '<img src="/static/img/Atencion/menosim.png" class="imagenIcono" title="-" onClick="eliminar('+emer+',';
            var mas       = '<img src="/static/img/Atencion/masim.png" class="imagenIcono" title="-" onClick="agregar('+emer+',';
            var checkbox  = '<input type="checkbox" onchange="estado('+emer+',';
            var check = ')" name="check" />';
            var checkbox2 = '<input type="checkbox" onchange="estado('+emer+',';
            var check2 = ')" name="check" checked />';
            $(".esperaC_"+emer).each(function(index,valor){
              $(valor).remove();
            });
            for (i = 0;i<esperasAsig.length;i++){
              if (esperasChecki[i]  == "0"){
                contenido=contenido+'<li id="'+emer+'-'+indexAsig[i]+'">'+'<span>'+menos+indexAsig[i]+')"/>'+'</span>'+checkbox+indexAsig[i]+check+imagenIni+indexAsig[i]+imagenFin+indexAsig[i]+finImagen+" "+esperasAsig[i]+"</li>";
                $('#causas_'+emer).before('<img id="img_'+emer+'_'+indexAsig[i]+'" style="width:50px;height:50px;" class = "esperaC_'+emer+'" src="/static/img/esperas/espera_'+indexAsig[i]+'.png"/>');
              }else if(esperasChecki[i] == "1"){
                contenido=contenido+'<li id="'+emer+'-'+indexAsig[i]+'">'+'<span>'+menos+indexAsig[i]+')"/>'+'</span>'+checkbox2+indexAsig[i]+check2+imagenIni+indexAsig[i]+imagenFin+indexAsig[i]+finImagen+" "+esperasAsig[i]+"</li>";
              }
            }
            contenido=contenido+'<hr id="hr'+emer+'">';
            var  j = 0;
            for (j = 0;j<esperasNasig.length;j++){
              contenido = contenido + '<li id="'+emer+'-'+indexNasig[j]+'">'+'<span>'+mas+indexNasig[j]+')"/>'+'</span>'+imagenIni+indexNasig[j]+imagenFin+indexNasig[j]+finImagen+" "+esperasNasig[j]+"</li>";
              i++;
            }
            $("#espera"+emer).attr('data-content',contenido);
          });
        });
      });
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
