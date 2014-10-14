$(document).ready(function () {
  /* botones 'X' que cierran los div*/
  /*se cierra la caja1*/
  $('#boton1').click(function(){
    $('#cajon1').slideUp();
  });

  /*Asociaciones de los botones*/
var On = 'On';
$('.NAD,.ABN').click(function(e){
  e.preventDefault();
  var input = $(this).attr('input');
  var b1 = true;
  var b2 = true;
  var padre1 = $(this).parents('table').find('.BNAD');
  var padre2 = $(this).parents('table').find('.BABN');
  var hijo1  = $(this).parents('table').find('.NAD');
  var hijo2  = $(this).parents('table').find('.ABN');
  $(this).toggleClass(On);
  if($(this).hasClass(On)){
    $(this).siblings().removeClass(On);
    if ( $(this).hasClass('ABN') ){ 
      $('#A'+input).show();
      $('#'+input).attr('value','anormal');
    }else { $('#A'+input).hide();
      $('#'+input).attr('value','normal');
    }

  }else{
    $(this).siblings().addClass(On);
    if ( $(this).hasClass('ABN') ){ 
      $('#A'+input).hide();
      $('#'+input).attr('value','normal');
    }else{ 
      $('#A'+input).show();
      $('#'+input).attr('value','anormal'); 
    }
  }

  hijo1.each(function(i,valor){
    if (!$(valor).hasClass(On)){
      padre1.removeClass(On);
      b1 = false;
    }
  });

  hijo2.each(function(i,valor){
    if (!$(valor).hasClass(On)){
      padre2.removeClass(On);
      b2 = false;
    }
  });

  if (b1){ padre1.addClass(On); }
  if (b2){ padre2.addClass(On); }

});

  $('.BNAD').click(function(e){
    e.preventDefault();
    $(this).toggleClass(On);
    $(this).siblings().removeClass(On);
    var hijos = $(this).parents('table').find('.NAD');
    var clase = $(this).hasClass(On); 

    if (clase){
      hijos.addClass(On);
      $(this).parents('table').find('.hide').hide();
      $(this).parents('table').find('input[type="hidden"]').attr('value','normal');
    }else{
      hijos.removeClass(On);
      $(this).parents('table').find('input[type="hidden"]').attr('value','no');
    }

    $(hijos).siblings().removeClass(On);

  });

  $('.BABN').click(function(e){
    e.preventDefault();
    $(this).toggleClass(On);
    $(this).siblings().removeClass(On);
    var hijos = $(this).parents('table').find('.ABN');
    var clase = $(this).hasClass(On); 
    
    if (clase){
      hijos.addClass(On);
      $(this).parents('table').find('.hide').show();
      $(this).parents('table').find('input[type="hidden"]').attr('value','anormal');
    }else{
      hijos.removeClass(On);
      $(this).parents('table').find('.hide').hide();
      $(this).parents('table').find('input[type="hidden"]').attr('value','no');
    }
    $(hijos).siblings().removeClass(On);

  });

});
