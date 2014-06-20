TDScopia
========

Sistema Centro Médico de Caracas(Itriage).

¿Qué es?
--------

El sistema de Itriage se creó con la finalidad de automarizar el proceso
de atención en la emergencia del Centro Médico de Caracas así como también
para proveer estadísticas acerca del tiempo de espera de los pacientes y proveer
además un módulo de historias médicas y reportes de información de la estadía de
los pacientes en la emergencia. 

Documentación
-------------

La documentación del sistema (tales como manuales de intalación y comandos 
útiles)se encuentra disponible en el reporsitorio, especificamente en la ruta 
/recursos para los comandos útiles y recursos/manuales para los manuales de 
instalación de Windows y Linux. Igualmente en la direccion de recursos puede encontrar
el archivo de los cambios y las nuevas funcionalidades que realizo el grupo 
anterior, ademas de toda la explicacion de la migracion de la base de datos,
en el archivo llamado entregaFinalTDS.pdf

Estructura del Repositorio
--------------------------

AM/ Carpeta donde se encuentran los archivos de configuración de la aplicación, 
tal como el settings.py y el urls.py.

BD/ Archivos de inserción para la base de datos. (Para insertar la información
de los archivos .json revisar el archivo /recursos/comantos.txt)

app_emergencia/ MVC y pruebas de la aplicación de emergencia que incluye 
todos los métodos que se utilizan en la emergencia, desde la aplicación del 
triage hasta generar un reporte en PDF de la atención realizada.

app_enfermedad/ MVC y pruebas para las enfermedades que se asignan a un paciente
al realizarle una atención. 

app_paciente/ MVC y pruebas para la información de los pacientes. 

app_perfil/ Controlador creado con la finalidad de mostrar un reporte en PDF del 
triage realizado a un paciente ingresado en la emergencia

app_registro/ Modelo creado para guardar la información relevante del registro 
de los usuarios en el sistema. 

app_usuario/ MVC y pruebas para los usuarios del sistema. En esta carpeta se
encuentra el CRUD, el manejo de sesiones y de privilegios de los usuarios. 

plantillas/ Listado de todas las vistas .html para la aplicaćión y archivos 
javascript.

recursos/ Documentación del sistema. 

  recursos/configuracion/ archivo settings.py de Django
  recursos/datagen/ archivos de generación de datos de prueba. 
  recursos/manuales Manuales de instalación para Windows y Linux

static/ Archivos CSS, JavaScript, Librerías e imágenes utilizadas en el sistema.



