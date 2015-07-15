function buena() {
  var currentTime = new Date()
  var mes = currentTime.getMonth() + 1;
  var dia = currentTime.getDate();
  var año = currentTime.getFullYear();
  
  var horas    = currentTime.getHours()
  var minutos  = currentTime.getMinutes()
  var segundos = currentTime.getSeconds()

  $("#id_ingreso").val(dia+"/"+mes+"/"+año+" "+horas+":"+minutos+":"+segundos)
}
