function buscarPaciente(str) {
    if ((str.length < 4) || (str == null) || (str == "")) {
	$("#listaPacientes").empty();
    } else {
	$.get("/pacientebuscarjson/"+str,function(data,status){
	    $("#listaPacientes").empty();
	    if (data.articulos != "") {
		
		for (var i = 0; i < articulos.length-1; i++) {
		    articulo = articulos[i].split(",");
		    a_id = articulo[0];
		    a_nombre = articulo[1];
		    a_precio = articulo[2];
		    a_img = articulo[3];
		    $("#listaAR").append("<li><a href='#' id='"+a_id+"' onclick='agregarVista("+a_id+",\""+a_nombre+"\","+a_precio+",1)' class='articulo articulo"+(i%2)+"'>"+a_img+"<div class='infoListaArticulo'><b>"+a_nombre+"</b> <br/>"+a_precio+" Bs.F</div><i class='icon-plus-sign'</a></li>");
		    
		}
	    }
	})
    }
};

