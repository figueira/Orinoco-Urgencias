function Efectos_Del_Avatar(emer){
  $('#ImageMap1').maphilight({fillColor: '63AFD0',strokeColor: 'ffffff',strokeWidth: 1,strokeOpacity: 0.3,fillOpacity: 0.5});
  //var colores = {Cabeza:morado,Pecho:azul,Brazos:rojo,Piernas:Amarillo,Abdomen:naranjaFF9F40,Pelvis:verde};
  var colores = {Cabeza:'C936D3',Pecho:'0C6E99',Brazos:'FF0000',Piernas:'FFFF00',Abdomen:'FF9900',Pelvis:'00FF00',Pies:'FFFF00',Manos:'FF0000',Cadera:'FFFF00',Hombros:'0000FF',Cuello:'C936D3'};

  $('.colorAzul').each(function(index,valor){
    var data = $(valor).data('maphilight') || {};
    data.fillColor = colores[$(valor).attr('id')];
    data.strokeColor   = colores[$(valor).attr('id')];
    data.strokeOpacity = 0.4;
    strokeWidth: 2;
    data.alwaysOn = true;
    data.fillOpacity = 0.18;
    $(valor).data('maphilight', data).trigger('alwaysOn.maphilight');    
  });

  $('.colorAzul').click(function(e) {
    e.preventDefault();
    var id = $(this).attr('id');
    $('.colorAzul').not(this).each(function(index,valor){
      var data = $(valor).data('maphilight') || {};
      data.fillColor = colores[$(valor).attr('id')];
      if ($(valor).attr('id') == id){
        data.fillOpacity = 0.6;
        data.strokeOpacity = 0.7;  
      }else{
        data.fillOpacity = 0.18;
        data.strokeOpacity = 0.4;
        strokeWidth: 2;
      }
    });
    
    var data = $(this).data('maphilight') || {};
    data.fillOpacity = 0.6;
    data.strokeOpacity = 0.7;
    //data.alwaysOn = !data.alwaysOn;
    // This sets the new data, and finally checks for areas with alwaysOn set
    $(this).data('maphilight', data).trigger('alwaysOn.maphilight');
  });

  $('#cajon1').hide();
  $('#General').click(function(){
    $('#cajon1').load('/emergencia/cuerpo/'+emer+'/Generales');
    $('#cajon1').slideDown(); 
    $("#cuerpou").scrollLeft(470); 
  });

  $('area').click(function(e){   
    e.preventDefault();          
    $('#cajon1').load('/emergencia/cuerpo/'+emer+'/'+$(this).attr('id'));
    $('#cajon1').slideDown(); 
    $("#cuerpou").scrollLeft(470);    
  });
}