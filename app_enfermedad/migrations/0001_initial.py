# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    
    depends_on = (
        ("app_emergencia", "0001_initial"),
    )
    def forwards(self, orm):
        # Adding model 'ParteCuerpo'
        db.create_table(u'app_enfermedad_partecuerpo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=48)),
        ))
        db.send_create_signal(u'app_enfermedad', ['ParteCuerpo'])

        # Adding model 'ZonaCuerpo'
        db.create_table(u'app_enfermedad_zonacuerpo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=48)),
        ))
        db.send_create_signal(u'app_enfermedad', ['ZonaCuerpo'])

        # Adding model 'Aspecto'
        db.create_table(u'app_enfermedad_aspecto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=48)),
        ))
        db.send_create_signal(u'app_enfermedad', ['Aspecto'])

        # Adding model 'AspectoAtencion'
        db.create_table(u'app_enfermedad_aspectoatencion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('revisado', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('aspecto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app_enfermedad.Aspecto'])),
            ('atencion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app_emergencia.Atencion'])),
        ))
        db.send_create_signal(u'app_enfermedad', ['AspectoAtencion'])

        # Adding model 'Anomalia'
        db.create_table(u'app_enfermedad_anomalia', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('descripcion', self.gf('django.db.models.fields.CharField')(max_length=48)),
            ('aspectoatencion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app_enfermedad.AspectoAtencion'])),
        ))
        db.send_create_signal(u'app_enfermedad', ['Anomalia'])

        # Adding model 'ZonaParte'
        db.create_table(u'app_enfermedad_zonaparte', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('partecuerpo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app_enfermedad.ParteCuerpo'])),
            ('zonacuerpo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app_enfermedad.ZonaCuerpo'])),
        ))
        db.send_create_signal(u'app_enfermedad', ['ZonaParte'])

        # Adding model 'ParteAspecto'
        db.create_table(u'app_enfermedad_parteaspecto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('aspecto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app_enfermedad.Aspecto'])),
            ('partecuerpo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app_enfermedad.ParteCuerpo'])),
        ))
        db.send_create_signal(u'app_enfermedad', ['ParteAspecto'])


    def backwards(self, orm):
        # Deleting model 'ParteCuerpo'
        db.delete_table(u'app_enfermedad_partecuerpo')

        # Deleting model 'ZonaCuerpo'
        db.delete_table(u'app_enfermedad_zonacuerpo')

        # Deleting model 'Aspecto'
        db.delete_table(u'app_enfermedad_aspecto')

        # Deleting model 'AspectoAtencion'
        db.delete_table(u'app_enfermedad_aspectoatencion')

        # Deleting model 'Anomalia'
        db.delete_table(u'app_enfermedad_anomalia')

        # Deleting model 'ZonaParte'
        db.delete_table(u'app_enfermedad_zonaparte')

        # Deleting model 'ParteAspecto'
        db.delete_table(u'app_enfermedad_parteaspecto')


    models = {
        u'app_emergencia.atencion': {
            'Meta': {'object_name': 'Atencion'},
            'area_atencion': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'emergencia': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Emergencia']"}),
            'fecha': ('django.db.models.fields.DateTimeField', [], {}),
            'fechaReal': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medico': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_usuario.Usuario']"})
        },
        u'app_emergencia.destino': {
            'Meta': {'object_name': 'Destino'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '48'})
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
        u'app_enfermedad.anomalia': {
            'Meta': {'object_name': 'Anomalia'},
            'aspectoatencion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_enfermedad.AspectoAtencion']"}),
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': '48'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'app_enfermedad.aspecto': {
            'Meta': {'object_name': 'Aspecto'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '48'})
        },
        u'app_enfermedad.aspectoatencion': {
            'Meta': {'object_name': 'AspectoAtencion'},
            'aspecto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_enfermedad.Aspecto']"}),
            'atencion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_emergencia.Atencion']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'revisado': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'app_enfermedad.parteaspecto': {
            'Meta': {'object_name': 'ParteAspecto'},
            'aspecto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_enfermedad.Aspecto']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'partecuerpo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_enfermedad.ParteCuerpo']"})
        },
        u'app_enfermedad.partecuerpo': {
            'Meta': {'object_name': 'ParteCuerpo'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '48'})
        },
        u'app_enfermedad.zonacuerpo': {
            'Meta': {'object_name': 'ZonaCuerpo'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '48'})
        },
        u'app_enfermedad.zonaparte': {
            'Meta': {'object_name': 'ZonaParte'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'partecuerpo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_enfermedad.ParteCuerpo']"}),
            'zonacuerpo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_enfermedad.ZonaCuerpo']"})
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

    complete_apps = ['app_enfermedad']