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

# Se cargan las enfermedades en la tabla
cursor.execute(open("../sql/enfermedades.sql", "r").read())
conn.commit()

cursor.close()
conn.close() 