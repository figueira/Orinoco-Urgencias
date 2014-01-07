from random import randint
from datetime import *
import nombres as nom


numero_de_pacientes = 100
numero_de_cubiculos = 30
numero_de_areas = 2
nombres = {}
apellidos = {}
cedula_inicial = 1111111
codigos_cel = ['0412','0414','0416']
codigo_casa = ['0212']
cantidad_nombres_masculinos = len(nom.nombres_masculinos)
cantidad_nombres_femeninos = len(nom.nombres_femeninos)
cantidad_apellidos = len(nom.apellidos)
maximo_tiempo_en_emergencia = 600
minimo_tiempo_en_emergencia = 20
maximo_tiempo_causa = 400
minimo_tiempo_causa = 10
cantidad_causas_espera = 10
pk_esperaemergencia = 1
estado = 0

final = '['

numero_cubiculo = 1
letra = 'A'
for pk_cubiculo in range(1, numero_de_cubiculos+1):
  nombre = str(numero_cubiculo)
  if (randint(0,1)):
    nombre += letra
    letra = chr(ord(letra) + 1)
  else:
    numero_cubiculo += 1
    letra = 'A'
  area = randint(1, numero_de_areas)
  cubiculo = '{"pk": %i, \n' % (pk_cubiculo, )
  cubiculo += '"model": "app_emergencia.cubiculo", \n"fields":\n{\n'
  cubiculo += '"nombre": "%s",\n' % (nombre, )
  cubiculo += '"area": %i\n' % (area, )
  cubiculo +='}\n},\n'
  final += cubiculo

for pk_paciente in range(1,numero_de_pacientes+1):
  es_hombre = randint(0,1) # 0 = FALSE
  contacto_es_hombre = randint(0,1) # 0 = FALSE
  cedula_inicial += 1
  
  tlf_cel = '%s%s' % (codigos_cel[randint(0,len(codigos_cel)-1)], randint(1111111,9999999))
  fecha_nacimiento = "%d-%02d-%02d" % (randint(1900, 2013), randint(1,12), randint(1,28))
  foto = ''
  signos_fc = 0 # PLACEHOLDER
  tlf_casa = '%s%s' % (codigo_casa[randint(0,len(codigo_casa)-1)], randint(1111111, 9999999))
  signos_pb = 0.0 # PLACEHOLDER
  
  if (es_hombre):
    nombres = nom.nombres_masculinos[randint(0, cantidad_nombres_masculinos-1)]
    nombres += ' ' + nom.nombres_masculinos[randint(0, cantidad_nombres_masculinos-1)]
    sexo = 1
  else:
    nombres = nom.nombres_femeninos[randint(0, cantidad_nombres_femeninos-1)]
    nombres += ' ' + nom.nombres_femeninos[randint(0, cantidad_nombres_femeninos-1)]
    sexo = 2
  
  if(contacto_es_hombre):
    contacto_nom = nom.nombres_masculinos[randint(0, cantidad_nombres_masculinos-1)]
  else:
    contacto_nom = nom.nombres_femeninos[randint(0, cantidad_nombres_femeninos-1)]
  contacto_rel = randint(1,11)
  contacto_nom += ' ' + nom.apellidos[randint(0, cantidad_apellidos-1)]
  signos_pa = 0 # PLACEHOLDER
  signos_saod = 0.0 # PLACEHOLDER
  apellidos = nom.apellidos[randint(0, cantidad_apellidos-1)]
  apellidos += ' ' + nom.apellidos[randint(0, cantidad_apellidos-1)]
  contacto_tlf = '%s%s' % (codigos_cel[randint(0,len(codigos_cel)-1)],\
    randint(1111111,9999999))
  signos_fr = 0 # PLACEHOLDER
  direccion = 'calle a, avenida b, ciudad c, estado d'
  email = nombres.replace(' ', '') + apellidos.replace(' ', '') +'@gmail.com'
  cedula = cedula_inicial
  signos_tmp = 0 # PLACEHOLDER
  
  
  
  paciente = '{"pk": %i, \n' % (pk_paciente, )
  paciente += '"model": "app_paciente.paciente",\n"fields":\n{\n'
  paciente += '"tlf_cel": "%s",\n'% (tlf_cel, )
  paciente += '"fecha_nacimiento": "%s",\n' % (fecha_nacimiento, )
  paciente += '"foto": "%s",\n' % (foto, )
  paciente += '"signos_fc": %i,\n' % (signos_fc, )
  paciente += '"tlf_casa": "%s",\n' % (tlf_casa, )
  paciente += '"signos_pb": %.1f,\n' % (signos_pb, )
  paciente += '"nombres": "%s",\n' % (nombres, )
  paciente += '"contacto_rel": %i,\n' % (contacto_rel, )
  paciente += '"signos_pa": %s,\n' % (signos_pa, )
  paciente += '"signos_saod": %.1f,\n' % (signos_saod, )
  paciente += '"sexo": %s,\n' % (sexo, )
  paciente += '"apellidos": "%s",\n' % (apellidos, )
  paciente += '"contacto_tlf": "%s",\n' % (contacto_tlf, )
  paciente += '"signos_fr": %i,\n' % (signos_fr, )
  paciente += '"contacto_nom": "%s",\n' % (contacto_nom, )
  paciente += '"direccion": "%s",\n' % (direccion, )
  paciente += '"email": "%s",\n' % (email, )
  paciente += '"cedula": "%s",\n' % (cedula, )
  paciente += '"signos_tmp": %.1f\n' % (signos_tmp, )
  paciente += '}\n},\n'
  
  final += paciente
  
  hora_diferencia = randint(12,24)
  fecha_hora_ayer = datetime.now() - timedelta(hours=hora_diferencia)
  tiempo_total_en_emergencia = randint(minimo_tiempo_en_emergencia,\
    maximo_tiempo_en_emergencia)
  
  
  pk_emergencia = pk_paciente
  destino = randint(1,5)
  hora_ingreso = str(fecha_hora_ayer).replace(' ', 'T')[:19]
  hora_ingresoReal = hora_ingreso
  egreso = 2
  responsable = 2
  ingreso = 2
  
  
  emergencia = '{"pk": %i,\n' % (pk_emergencia, )
  emergencia += '"model": "app_emergencia.emergencia",\n"fields":\n{\n'
  emergencia += '"destino": %i,\n' % (destino, )
  emergencia += '"hora_ingreso": "%s",\n' % (hora_ingreso, )
  emergencia += '"paciente": %i,\n' % (pk_paciente, )
  emergencia += '"hora_ingresoReal": "%s",\n' % (hora_ingresoReal, )
  emergencia += '"egreso": %i,\n' % (egreso, )
  emergencia += '"responsable": %i,\n' % (responsable, )
  emergencia += '"ingreso": %i,\n' % (ingreso, )
  
  primera = True
  tiempo_acumulado = 0
  espera_emergencia = ''
  hora_actual = fecha_hora_ayer
  
  for causa in range(1,cantidad_causas_espera+1):
    tiene_causa = randint(0,1)
    if (tiene_causa and (tiempo_acumulado < maximo_tiempo_en_emergencia)):
      duracion_de_causa = randint(0, maximo_tiempo_causa - tiempo_acumulado)
      tiempo_acumulado += duracion_de_causa
      if (primera):
	primera = False
      else:
	espera_emergencia += ',\n'
      hora_comienzo = str(hora_actual).replace(' ','T')[:19]
      
      espera_emergencia += '{"pk": %i,\n' % (pk_esperaemergencia, )
      espera_emergencia += '"model": "app_emergencia.esperaemergencia",\n"fields":\n{\n'
      espera_emergencia += '"estado": %i,\n' % (estado, )
      espera_emergencia += '"hora_comienzo": "%s",\n' % (hora_comienzo, )
      
      hora_actual = hora_actual + timedelta(minutes=duracion_de_causa)
      hora_fin = str(hora_actual).replace(' ', 'T')[:19]
      
      espera_emergencia += '"hora_fin": "%s",\n' % (hora_fin, )
      espera_emergencia += '"espera": %i,\n' % (causa, )
      espera_emergencia += '"emergencia": %i\n' % (pk_emergencia, )
      espera_emergencia += '}\n}\n'
      pk_esperaemergencia += 1
      
  
  hora_egreso = str(fecha_hora_ayer+timedelta(minutes=tiempo_acumulado))\
    .replace(' ','T')[:19]
  hora_egresoReal = hora_egreso
  fecha_Esp_act = hora_egresoReal
  
  emergencia += '"hora_egresoReal": "%s",\n' % (hora_egresoReal, )
  emergencia += '"hora_egreso": "%s",\n' % (hora_egreso, )
  emergencia += '"fecha_Esp_act": "%s"\n' % (fecha_Esp_act, )
  emergencia += '}\n},\n'
  
  
  
  
  final += emergencia
  final += espera_emergencia
  if (pk_paciente != numero_de_pacientes):
    final += ','
final += ']'
  
print '%s' % (final, ) 
