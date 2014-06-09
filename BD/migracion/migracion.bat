python edicionTablas.py
python ../../manage.py dumpdata auth.user app_usuario.usuario app_paciente.paciente app_emergencia.emergencia app_emergencia.triage app_emergencia.atencion app_emergencia.esperaemergencia > BDbackup.json 
python eliminacionTablas.py
python ../../manage.py syncdb
python ../../manage.py loaddata ..\aadmision.json
python ../../manage.py loaddata ..\aemergencia.json
python ../../manage.py loaddata ..\at_indicaciones.json
python ../../manage.py loaddata ..\atencion_cuerpo_sintomas.json
python ../../manage.py loaddata ..\cubiculo.json
python ../../manage.py loaddata ..\edestino.json
python ../../manage.py loaddata ..\espera.json
python ../../manage.py loaddata ..\motivos.json
python loadEnfermedades.py
python ../../manage.py loaddata BDbackup.json