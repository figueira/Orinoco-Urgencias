 function Fspin(div_spin){
  var opts = {lines: 7,length: 6,width: 7, radius: 7, corners: 1,
    rotate: 0,
    direction: 1, // 1: clockwise, -1: counterclockwise
    color: '#2f96b4', // #rgb or #rrggbb
    speed: 1, trail: 160, shadow: false, hwaccel: true,className: 'spinner',
    zIndex: 2e9,top: 'auto', left: 'auto'
  };
  var target = document.getElementById(div_spin);
  var spinner = new Spinner(opts).spin(target);
  $('#'+div_spin).data('spinner', spinner);
}

function loadAtencion(emer){
  $('#dEnf').load('/emergencia/enf_actual/'+emer);
  
  $('#aAnt').click(function(){
    $('#Ant2').load('/emergencia/antecedente/'+emer);
  });
  
  $('#aEfis').click(function(){
    Fspin('spinCuerpo');
    $('#Efis').load('/emergencia/enfermedad/'+emer);
  });

  $('#aInd').click(function(){
    $("#d_But").load("/emergencia/indi/"+emer);
  });

  $('#aDiag').click(function(){
    $('#dDiag').load('/emergencia/diagnostico/'+emer);
  });
}

/* atencion_ant_medica */
function envia(pag){
  var formu = $('#formu').serialize();
  Fspin('Dant');
  $.post(pag,formu,function(data){  
    $("#Dant").html(data);
    $('#Dant').data('spinner').stop();
  });
}

function CompruebaCampo(obj,clonLast){
    if ($(obj).parents("tr").hasClass("ultimo")){
      var ultimo = $(".ultimo:last");
      ultimo.removeClass("ultimo");
      var clonte = clonLast.clone();
      clonte.insertAfter($(ultimo));
    }
}