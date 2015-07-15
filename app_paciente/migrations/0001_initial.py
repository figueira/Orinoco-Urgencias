# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = (
        ("app_usuario", "0001_initial"),
    )
    def forwards(self, orm):
        # Adding model 'Enfermedad'
        db.create_table(u'app_paciente_enfermedad', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=10, primary_key=True)),
            ('descripcion', self.gf('django.db.models.fields.CharField')(max_length=400)),
            ('grupo', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'app_paciente', ['Enfermedad'])

        # Adding model 'Paciente'
        db.create_table(u'app_paciente_paciente', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cedula', self.gf('django.db.models.fields.TextField')(default=0, unique=True)),
            ('nombres', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('apellidos', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('sexo', self.gf('django.db.models.fields.IntegerField')()),
            ('fecha_nacimiento', self.gf('django.db.models.fields.DateField')()),
            ('tlf_cel', self.gf('django.db.models.fields.CharField')(max_length=11)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('direccion', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('tlf_casa', self.gf('django.db.models.fields.CharField')(max_length=11)),
            ('contacto_rel', self.gf('django.db.models.fields.IntegerField')()),
            ('contacto_nom', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('contacto_tlf', self.gf('django.db.models.fields.CharField')(max_length=11)),
            ('foto', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'app_paciente', ['Paciente'])

        # Adding M2M table for field enfermedades on 'Paciente'
        m2m_table_name = db.shorten_name(u'app_paciente_paciente_enfermedades')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('paciente', models.ForeignKey(orm[u'app_paciente.paciente'], null=False)),
            ('enfermedad', models.ForeignKey(orm[u'app_paciente.enfermedad'], null=False))
        ))
        db.create_unique(m2m_table_name, ['paciente_id', 'enfermedad_id'])

        # Adding model 'Antecedente'
        db.create_table(u'app_paciente_antecedente', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tipo', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'app_paciente', ['Antecedente'])

        # Adding model 'Pertenencia'
        db.create_table(u'app_paciente_pertenencia', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('paciente', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app_paciente.Paciente'])),
            ('antecedente', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app_paciente.Antecedente'])),
        ))
        db.send_create_signal(u'app_paciente', ['Pertenencia'])

        # Adding model 'Lugar'
        db.create_table(u'app_paciente_lugar', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'app_paciente', ['Lugar'])

        # Adding model 'LugarPertenencia'
        db.create_table(u'app_paciente_lugarpertenencia', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pertenencia', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app_paciente.Pertenencia'])),
            ('lugar', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app_paciente.Lugar'])),
        ))
        db.send_create_signal(u'app_paciente', ['LugarPertenencia'])

        # Adding model 'Tratamiento'
        db.create_table(u'app_paciente_tratamiento', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'app_paciente', ['Tratamiento'])

        # Adding model 'TratamientoPertenencia'
        db.create_table(u'app_paciente_tratamientopertenencia', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pertenencia', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app_paciente.Pertenencia'])),
            ('tratamiento', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app_paciente.Tratamiento'])),
        ))
        db.send_create_signal(u'app_paciente', ['TratamientoPertenencia'])

        # Adding model 'Fecha'
        db.create_table(u'app_paciente_fecha', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fecha', self.gf('django.db.models.fields.DateField')()),
            ('pertenencia', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app_paciente.Pertenencia'])),
        ))
        db.send_create_signal(u'app_paciente', ['Fecha'])


    def backwards(self, orm):
        # Deleting model 'Enfermedad'
        db.delete_table(u'app_paciente_enfermedad')

        # Deleting model 'Paciente'
        db.delete_table(u'app_paciente_paciente')

        # Removing M2M table for field enfermedades on 'Paciente'
        db.delete_table(db.shorten_name(u'app_paciente_paciente_enfermedades'))

        # Deleting model 'Antecedente'
        db.delete_table(u'app_paciente_antecedente')

        # Deleting model 'Pertenencia'
        db.delete_table(u'app_paciente_pertenencia')

        # Deleting model 'Lugar'
        db.delete_table(u'app_paciente_lugar')

        # Deleting model 'LugarPertenencia'
        db.delete_table(u'app_paciente_lugarpertenencia')

        # Deleting model 'Tratamiento'
        db.delete_table(u'app_paciente_tratamiento')

        # Deleting model 'TratamientoPertenencia'
        db.delete_table(u'app_paciente_tratamientopertenencia')

        # Deleting model 'Fecha'
        db.delete_table(u'app_paciente_fecha')


    models = {
        u'app_paciente.antecedente': {
            'Meta': {'object_name': 'Antecedente'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'app_paciente.enfermedad': {
            'Meta': {'object_name': 'Enfermedad'},
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'grupo': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '10', 'primary_key': 'True'})
        },
        u'app_paciente.fecha': {
            'Meta': {'object_name': 'Fecha'},
            'fecha': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pertenencia': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_paciente.Pertenencia']"})
        },
        u'app_paciente.lugar': {
            'Meta': {'object_name': 'Lugar'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'app_paciente.lugarpertenencia': {
            'Meta': {'object_name': 'LugarPertenencia'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lugar': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_paciente.Lugar']"}),
            'pertenencia': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_paciente.Pertenencia']"})
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
        u'app_paciente.pertenencia': {
            'Meta': {'object_name': 'Pertenencia'},
            'antecedente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_paciente.Antecedente']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'paciente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_paciente.Paciente']"})
        },
        u'app_paciente.tratamiento': {
            'Meta': {'object_name': 'Tratamiento'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'app_paciente.tratamientopertenencia': {
            'Meta': {'object_name': 'TratamientoPertenencia'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pertenencia': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_paciente.Pertenencia']"}),
            'tratamiento': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['app_paciente.Tratamiento']"})
        }
    }

    complete_apps = ['app_paciente']