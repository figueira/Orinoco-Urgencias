import psycopg2
import psycopg2.extras
import sys
import json
  
# Se define el string de conexion
conn_string = "host='localhost' dbname='cmsb' user='postgres' password='postgres'"

# Se conecta a la BD
try:
	conn = psycopg2.connect(conn_string)
except:
	print "No se pudo conectar a la BD"

# conn.cursor regresa un cursor object que permite realizar queries. 
# DictCursor permite obtener los atributos de los objetos por los nombres
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Se modifca la tabla de triage
cursor.execute("ALTER TABLE app_emergencia_triage ALTER COLUMN signos_fc TYPE integer") 
cursor.execute("ALTER TABLE app_emergencia_triage ALTER COLUMN signos_saod TYPE integer") 
conn.commit()

# Se obtienen los pacientes 
cursor.execute("SELECT * FROM app_paciente_paciente ORDER BY id") 
pacientes = cursor.fetchall()

for paciente in pacientes:	
	# Se buscan todos los triages de este paciente ordenados descendientemente por la hora de egreso
	cursor.execute("SELECT t.id, t.emergencia_id, t.medico_id, t.fecha, t.\"fechaReal\", t.motivo_id, t.\"areaAtencion_id\",\
	t.ingreso, t.atencion, t.esperar, t.recursos, t.nivel\
	FROM app_emergencia_emergencia e, app_emergencia_triage t\
	WHERE e.paciente_id ="+str(paciente['id'])+"\
	AND t.emergencia_id = e.id\
	ORDER BY e.hora_egreso DESC") 
	triages = cursor.fetchall()
		
	ultimoTriage = True
	for triage in triages:		
		# Al ultimo triage se le coloca los signos vitales que habia en paciente y al resto se le coloca valor de invalido
		if ultimoTriage:
			query = "UPDATE app_emergencia_triage SET\
			signos_tmp=" + str(paciente['signos_tmp']) + ",\
			signos_fc=" + str(int(paciente['signos_fc'])) + ",\
			signos_fr=" + str(paciente['signos_fr']) + ",\
			signos_pa=" + str(paciente['signos_pa']) + ",\
			signos_pb=" + str(paciente['signos_pb']) + ",\
			signos_saod=" + str(int(paciente['signos_saod'])) + ","			
			ultimoTriage = False
		else:
			query = "UPDATE app_emergencia_triage SET\
			signos_tmp= -1,\
			signos_fc= -1,\
			signos_fr= -1,\
			signos_pa= -1,\
			signos_pb= -1,\
			signos_saod= -1,"
		
		query = query + "signos_avpu='N', signos_dolor=-1 WHERE id="+str(triage['id'])
		cursor.execute(query) 
		conn.commit()
		
# Borro los campos de signos de la tabla de paciente
cursor.execute("ALTER TABLE app_paciente_paciente DROP COLUMN signos_tmp") 
cursor.execute("ALTER TABLE app_paciente_paciente DROP COLUMN signos_fc") 
cursor.execute("ALTER TABLE app_paciente_paciente DROP COLUMN signos_fr") 
cursor.execute("ALTER TABLE app_paciente_paciente DROP COLUMN signos_pa") 
cursor.execute("ALTER TABLE app_paciente_paciente DROP COLUMN signos_pb") 
cursor.execute("ALTER TABLE app_paciente_paciente DROP COLUMN signos_saod") 
conn.commit()



# Se obtienen los CI de los pacientes repetidos
cursor.execute("SELECT cedula FROM app_paciente_paciente GROUP BY cedula HAVING count(cedula)>1 ORDER BY cedula") 
ciPacientes = cursor.fetchall()
for cip in ciPacientes:	

	# Se busca el ID del paciente repetido
	cursor.execute("SELECT id FROM app_paciente_paciente WHERE cedula='"+str(cip['cedula'])+"'") 
	idPaciente = cursor.fetchall()
	idPa = -1
	for idp in idPaciente:
	
		# Se buscan todas las emergencias de ese paciente
		cursor.execute("SELECT id FROM app_emergencia_emergencia WHERE paciente_id='"+str(idp['id'])+"'") 
		emergencias = cursor.fetchall()	
		numEmer = len(emergencias)
		for emer in emergencias:
		
			# Se busca el triage de la emergencia
			cursor.execute("SELECT id FROM app_emergencia_triage WHERE emergencia_id='"+str(emer['id'])+"'") 
			triages = cursor.fetchall()			
			if len(triages)<=0:
				cursor.execute("DELETE FROM app_emergencia_emergencia WHERE id='"+str(emer['id'])+"'") 
				cursor.execute("DELETE FROM app_emergencia_atencion WHERE emergencia_id='"+str(emer['id'])+"'") 
				cursor.execute("DELETE FROM app_emergencia_esperaemergencia WHERE emergencia_id='"+str(emer['id'])+"'") 
				conn.commit()
				numEmer = numEmer - 1

		if numEmer<=0:
			cursor.execute("DELETE FROM app_paciente_paciente WHERE id='"+str(idp['id'])+"'") 
			cursor.execute("DELETE FROM app_paciente_paciente_enfermedades WHERE paciente_id='"+str(idp['id'])+"'") 
			conn.commit()
		else:
			if idPa==-1:
				idPa = idp['id']
			else:
				cursor.execute("DELETE FROM app_paciente_paciente WHERE id='"+str(idp['id'])+"'") 
				cursor.execute("DELETE FROM app_paciente_paciente_enfermedades WHERE paciente_id='"+str(idp['id'])+"'") 
				cursor.execute("UPDATE app_emergencia_emergencia SET paciente_id='"+str(idPa)+"' WHERE paciente_id='"+str(idp['id'])+"'") 
				conn.commit()
				
cursor.close()
conn.close() 