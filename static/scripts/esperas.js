/* 
  Hace que una serie de causas de espera se mantengan activas
  Entrada:
    El objeto de jQuery correspondiente a la fila en la que la espera se 
    imprime
*/
function MantenerEsperas(fila_emergencia){
  var id_emergencia = fila_emergencia.data('id-emergencia');
  fila_emergencia.data("tiempoesp", 0);
  fila_emergencia.data("tiempo_espera_inicio","0");
  fila_emergencia.css("background","white");
  $.get("/emergencia/espera_mantener/" + id_emergencia);
}
