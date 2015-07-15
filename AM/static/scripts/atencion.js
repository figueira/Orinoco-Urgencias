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

function envia2(pag){
    $('#Dant').load(pag);
}

var numErrores = 0;

function mandarInfo2(dir){
	numErrores=0;
	envia2(dir);
}

function CompruebaCampo(obj,clonLast,tipo_ant){
	padre = $(obj).parents("tr");
	if (padre.hasClass("ultimo")){			
		var duplicar = false;
		var nuevoNombre = padre.find("#id_nuevoNombre").val();		
		
		if(tipo_ant=='medica' || tipo_ant=='quirurgica'){
			var fecha = padre.find("#id_fecha");
			var nuevoAtributo = padre.find("#id_nuevoAtributo3").val();
			
			if(nuevoNombre!="" && fecha.val()!="" && nuevoAtributo!=""){		
				duplicar = true;
			}
		}else{
			if(nuevoNombre!=""){
				duplicar = true;
			}
		}
		
		if(duplicar){
			var ultimo = $(".ultimo:last");
			ultimo.removeClass("ultimo");
			var clonte = clonLast.clone();
			clonte.insertAfter($(ultimo));
		}    
	}
}

function validarFecha(fecha){
	// dd/mm/aaaa
	var formato = /^(0?[1-9]|[12][0-9]|3[01])[\/](0?[1-9]|1[012])[\/]\d{4}$/;
	fecha.value = fecha.value.trim();
	if(!fecha.value.match(formato)) { 
		$(fecha).addClass('errorCampoAnte');
		numErrores++;
	}else{
		if ($(fecha).hasClass("errorCampoAnte")){
			$(fecha).removeClass('errorCampoAnte');
			numErrores--;
		}		
	}
}

function validarCampo(campo){
	if(campo.value.trim()=="") { 
		$(campo).addClass('errorCampoAnte');
		numErrores++;
	}else{
		if ($(campo).hasClass("errorCampoAnte")){
			$(campo).removeClass('errorCampoAnte');
			numErrores--;
		}
	}
}

function mandarInfo(dir){
	if(numErrores==0)
	{
		envia(dir);
	}
}
