# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Cubiculo.emergencia'
        db.add_column(u'app_emergencia_cubiculo', 'emergencia',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['app_emergencia.Emergencia'], unique=True, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Cubiculo.emergencia'
        db.delete_column(u'app_emergencia_cubiculo', 'emergencia_id')


    models = {
        u'app_emergencia.admision': {
            'Meta': {'object_name': 'Admision'},
            'area': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.AreaAdmision']"}),
            'emergencia': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Emergencia']"}),
            'hora_ingreso': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'hora_ingresoReal': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'app_emergencia.areaadmision': {
            'Meta': {'object_name': 'AreaAdmision'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '48'})
        },
        u'app_emergencia.areaemergencia': {
            'Meta': {'object_name': 'AreaEmergencia'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '48'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'app_emergencia.asignar': {
            'Meta': {'object_name': 'Asignar'},
            'emergencia': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Emergencia']"}),
            'fecha': ('django.db.models.fields.DateTimeField', [], {}),
            'fechaReal': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicacion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Indicacion']"}),
            'persona': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_usuario.Usuario']"}),
            'status': ('django.db.models.fields.IntegerField', [], {})
        },
        u'app_emergencia.asignarcub': {
            'Meta': {'object_name': 'AsignarCub'},
            'cubiculo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Cubiculo']"}),
            'emergencia': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Emergencia']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'app_emergencia.atencion': {
            'Meta': {'object_name': 'Atencion'},
            'area_atencion': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'emergencia': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Emergencia']"}),
            'fecha': ('django.db.models.fields.DateTimeField', [], {}),
            'fechaReal': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medico': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_usuario.Usuario']"})
        },
        u'app_emergencia.combinarhidrata': {
            'Meta': {'object_name': 'CombinarHidrata'},
            'hidratacion1': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.EspHidrata']", 'null': 'True'}),
            'hidratacion2': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Indicacion']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'app_emergencia.comentarioemergencia': {
            'Meta': {'object_name': 'ComentarioEmergencia'},
            'comentario': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'emergencia': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Emergencia']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'app_emergencia.comentariotriage': {
            'Meta': {'object_name': 'ComentarioTriage'},
            'comentario': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'triage': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Triage']"})
        },
        u'app_emergencia.cubiculo': {
            'Meta': {'object_name': 'Cubiculo'},
            'area': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.AreaEmergencia']"}),
            'emergencia': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['app_emergencia.Emergencia']", 'unique': 'True', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '48'})
        },
        u'app_emergencia.destino': {
            'Meta': {'object_name': 'Destino'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '48'})
        },
        u'app_emergencia.diagnostico': {
            'Meta': {'object_name': 'Diagnostico'},
            'atencion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Atencion']"}),
            'enfermedad': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_paciente.Enfermedad']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'app_emergencia.emergencia': {
            'Meta': {'object_name': 'Emergencia'},
            'destino': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Destino']", 'null': 'True', 'blank': 'True'}),
            'egreso': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'De alta por'", 'null': 'True', 'to': u"orm['app_usuario.Usuario']"}),
            'fecha_Esp_act': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hora_egreso': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'hora_egresoReal': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'hora_ingreso': ('django.db.models.fields.DateTimeField', [], {}),
            'hora_ingresoReal': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ingreso': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Ingresado por'", 'to': u"orm['app_usuario.Usuario']"}),
            'paciente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_paciente.Paciente']"}),
            'responsable': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'A cargo'", 'to': u"orm['app_usuario.Usuario']"})
        },
        u'app_emergencia.enfermedadactual': {
            'Meta': {'object_name': 'EnfermedadActual'},
            'atencion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Atencion']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'narrativa': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'app_emergencia.espdieta': {
            'Meta': {'object_name': 'EspDieta'},
            'asignacion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Asignar']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'observacion': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'})
        },
        u'app_emergencia.espera': {
            'Meta': {'object_name': 'Espera'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '48'})
        },
        u'app_emergencia.esperaemergencia': {
            'Meta': {'object_name': 'EsperaEmergencia'},
            'emergencia': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Emergencia']"}),
            'espera': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Espera']"}),
            'estado': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'hora_comienzo': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hora_fin': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'app_emergencia.esphidrata': {
            'Meta': {'object_name': 'EspHidrata'},
            'asignacion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Asignar']"}),
            'complementos': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vel_inf_unidad': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'vel_infusion': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'volumen': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'app_emergencia.espimg': {
            'Meta': {'object_name': 'EspImg'},
            'asignacion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Asignar']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parte_cuerpo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'app_emergencia.espmedics': {
            'Meta': {'object_name': 'EspMedics'},
            'asignacion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Asignar']"}),
            'dosis': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'frecuencia': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tipo_conc': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'tipo_frec': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'}),
            'via_admin': ('django.db.models.fields.CharField', [], {'max_length': '13', 'blank': 'True'})
        },
        u'app_emergencia.indicacion': {
            'Meta': {'object_name': 'Indicacion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'app_emergencia.motivo': {
            'Meta': {'object_name': 'Motivo'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '48'})
        },
        u'app_emergencia.tienesos': {
            'Meta': {'object_name': 'tieneSOS'},
            'comentario': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'espMed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.EspMedics']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'situacion': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'app_emergencia.triage': {
            'Meta': {'object_name': 'Triage'},
            'areaAtencion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.AreaEmergencia']", 'blank': 'True'}),
            'atencion': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'emergencia': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Emergencia']"}),
            'esperar': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fecha': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'fechaReal': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ingreso': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'medico': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_usuario.Usuario']"}),
            'motivo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Motivo']", 'blank': 'True'}),
            'nivel': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'recursos': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'signos_avpu': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'signos_dolor': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'signos_fc': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'signos_fr': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'signos_pa': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'signos_pb': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'signos_saod': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'signos_tmp': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'})
        },
        u'app_paciente.enfermedad': {
            'Meta': {'object_name': 'Enfermedad'},
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'grupo': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '10', 'primary_key': 'True'})
        },
        u'app_paciente.paciente': {
            'Meta': {'object_name': 'Paciente'},
            'apellidos': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'cedula': ('django.db.models.fields.TextField', [], {'default': '0', 'unique': 'True'}),
            'contacto_nom': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'contacto_rel': ('django.db.models.fields.IntegerField', [], {}),
            'contacto_tlf': ('django.db.models.fields.CharField', [], {'max_length': '11'}),
            'direccion': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'enfermedades': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['app_paciente.Enfermedad']", 'symmetrical': 'False', 'blank': 'True'}),
            'fecha_nacimiento': ('django.db.models.fields.DateField', [], {}),
            'foto': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombres': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'sexo': ('django.db.models.fields.IntegerField', [], {}),
            'tlf_casa': ('django.db.models.fields.CharField', [], {'max_length': '11'}),
            'tlf_cel': ('django.db.models.fields.CharField', [], {'max_length': '11'})
        },
        u'app_usuario.usuario': {
            'Meta': {'object_name': 'Usuario', '_ormbases': [u'auth.User']},
            'administrador': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cedula': ('django.db.models.fields.IntegerField', [], {'default': '0', 'unique': 'True'}),
            'direccion': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'habilitado': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sexo': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'tlf_casa': ('django.db.models.fields.CharField', [], {'max_length': '11'}),
            'tlf_cel': ('django.db.models.fields.CharField', [], {'max_length': '11'}),
            u'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['app_emergencia']