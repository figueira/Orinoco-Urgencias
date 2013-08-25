function cargar(emer,parteC){
	Fspin('cajon1');
	var formu = $('#formularioCuerpo').serialize();
	$.post('/emergencia/enviarcuerpo/'+emer+'/'+parteC,formu, 
		function(){
	  		$('#cajon1').data('spinner').stop();
	});
}

function botones_sintomas(){
	$('#'+'ejemplo').hide();
    $('.hide').hide();
    var bon  = true;
    var boff = true;
    var padre1 = $('table').find('.BNAD');
    var padre2 = $('table').find('.BABN');
    $('input[type="hidden"]').each(function(index,valor){
      var estado = $(valor).attr('value');
      var nombre = $(valor).attr('id');
      if (estado=='normalN'){
        $('#p'+nombre+'1').addClass('On');
        boff = false;
      }else if(estado=='anormalN'){
        $('#p'+nombre+'2').addClass('On');
        $('#A'+nombre).show();
        bon = false;
      }else if(estado=='noN'){
        bon  = false;
        boff = false;
      }
     
    });
    if (bon){ 
      padre1.addClass('On'); 
    }
    if (boff){ padre2.addClass('On'); }
}