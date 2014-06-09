import psycopg2
import sys

# Se define el string de conexion
conn_string = "host='localhost' dbname='cmsb' user='postgres' password='postgres'"

# Se conecta a la BD
try:
	conn = psycopg2.connect(conn_string)
except:
	print "No se pudo conectar a la BD"

# conn.cursor regresa un cursor object que permite realizar queries. 
cursor = conn.cursor()

# Se elminan todas las tablas de la BD
cursor.execute("SELECT table_schema,table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_schema,table_name")
tablas = cursor.fetchall()
for tabla in tablas: 
	cursor.execute("DROP TABLE " + tabla[1] + " CASCADE") 
	conn.commit()
	
cursor.close()
conn.close() 