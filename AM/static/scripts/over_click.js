 $(document).ready(function() {
    var clase_activo = 'boton-on';
    var clase_normal = 'boton-off';

    $('.'+clase_normal).click(function(){
                     
        if($(this).hasClass(clase_normal)){
            $(this).toggleClass(clase_normal);
            $(this).addClass(clase_activo);
            $('.'+clase_normal+','+' .'+clase_activo).not(this).each(function(i,valor) {
               if ($(valor).hasClass(clase_activo)){
                    $(valor).toggleClass(clase_activo);                
                    $(valor).addClass(clase_normal);
               }
            });

        } else{
            $(this).toggleClass(clase_activo);                
            $(this).addClass(clase_normal);
        }
    });

});