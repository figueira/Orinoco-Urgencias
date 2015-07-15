function parteCuerpo(parte_cuerpo,emer){
	Fspin('cajon1');
	$('#div_Parte_Cuerpo').load('/emergencia/partecuerpo/'+emer+'/'+parte_cuerpo,function(){
	   $('#cajon1').data('spinner').stop();
	});  
}

function inputs_de_anomalias(){
  $('#'+'ejemplo').hide();
    $('.hide').hide();

    $('input[type="hidden"]').each(function(index,valor){
      var estado = $(valor).attr('value');
      var nombre = $(valor).attr('id');
      if (estado=='normalN'){
        $('#p'+nombre+'1').addClass('On');
      }else if(estado=='anormalN'){
        $('#p'+nombre+'2').addClass('On');
        $('#A'+nombre).show();
      }
    });
}