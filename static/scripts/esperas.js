function estado(emer,i){
  var estado="";
  var num = parseInt($('#texto'+emer).attr("texto"));
  if($("#"+emer+'-'+i).find('input').is(':checked')) {num = num-1;estado ="1";}
  else {num = num+1;estado="0";}

  $('#texto'+emer).attr("texto",num);
  $('#texto'+emer).html("&nbsp;"+num+"&nbsp;&nbsp;"); 
  $.get("/emergencia/espera_estado/"+emer+"/"+i+"/"+estado);
}

function eliminar(emer,i){
  var num = parseInt($('#texto'+emer).attr("texto"));
  if(!$("#"+emer+'-'+i).find('input').is(':checked')){
    num = num-1;
    $('#texto'+emer).attr("texto",num);
    $('#texto'+emer).html("&nbsp;"+num+"&nbsp;&nbsp;");
  }
  
  $('#'+emer+'-'+i).insertAfter($('#hr'+emer));
  $('#'+emer+'-'+i).find('img').attr('src','/static/img/Atencion/masim.png');
  $('#'+emer+'-'+i).find('img').attr('onClick','agregar('+emer+','+i+')');
  $('#'+emer+'-'+i).find('input').remove();
  $.get("/emergencia/espera_eliminar/"+emer+"/"+i);
}

function agregar(emer,i){
  var num = parseInt($('#texto'+emer).attr("texto"))+1;
  $('#texto'+emer).attr("texto",num);
  $('#texto'+emer).html("&nbsp;"+num+"&nbsp;&nbsp;");

  $('#'+emer+'-'+i).insertBefore($('#hr'+emer));
  $('#'+emer+'-'+i).find('img').attr('src','/static/img/Atencion/menosim.png');
  $('#'+emer+'-'+i).find('img').attr('onClick','eliminar('+emer+','+i+')');

  $('#'+emer+'-'+i).find('input').show();
  $('#'+emer+'-'+i).find('a').after('<input type="checkbox" onchange="estado('+emer+','+i+')" name="check" value="{{i.antecedente.id}}" />');
  $.get("/emergencia/espera_agregar/"+emer+"/"+i);
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

            var indexNasig    = data5.substring(0,data5.length-1);
            if(indexNasig == "" ){indexNasig = [];}
            else{indexNasig = indexNasig.split(",");}

            var tamano1 = esperasAsig.length +esperasNasig.length;
            if (tamano1 != 6){alert("tamano malo = "+tamano1+"\n"+"data1 = "+esperasAsig.length+"\n"+esperasAsig+"\ndata2 = "+esperasNasig.length+"\n"+esperasNasig);}

            var i = 0;
            var contenido = "";
            var menos     = '<img src="/static/img/Atencion/menosim.png" title="-" onClick="eliminar('+emer+',';
            var mas       = '<img src="/static/img/Atencion/masim.png" title="-" onClick="agregar('+emer+',';
            var checkbox  = '<input type="checkbox" onchange="estado('+emer+',';
            var check = ')" name="check" />';
            var checkbox2 = '<input type="checkbox" onchange="estado('+emer+',';
            var check2 = ')" name="check" checked />';

            for (i = 0;i<esperasAsig.length;i++){
              if (esperasChecki[i]  == "0"){
                contenido=contenido+'<li id="'+emer+'-'+indexAsig[i]+'">'+'<a href="#">'+menos+indexAsig[i]+')"/>'+'</a>'+checkbox+indexAsig[i]+check+" "+esperasAsig[i]+"</li>";
              }else if(esperasChecki[i] == "1"){
                contenido=contenido+'<li id="'+emer+'-'+indexAsig[i]+'">'+'<a href="#">'+menos+indexAsig[i]+')"/>'+'</a>'+checkbox2+indexAsig[i]+check2+" "+esperasAsig[i]+"</li>";
              }
            }
            contenido=contenido+'<hr id="hr'+emer+'">';
            var j = 0;
            for (j = 0;j<esperasNasig.length;j++){
              contenido=contenido+'<li id="'+emer+'-'+indexNasig[j]+'">'+'<a href="#">'+mas+indexNasig[j]+')"/>'+'</a>'+" "+esperasNasig[j]+"</li>";
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
  });

  $('.espera').click(function(){
    contenido($(this).attr('idEmer'));  
  });
});