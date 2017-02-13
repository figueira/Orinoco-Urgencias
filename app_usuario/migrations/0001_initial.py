# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.contrib.auth.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('user_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('cedula', models.IntegerField(default=0, unique=True)),
                ('tipo', models.CharField(max_length=1, choices=[(b'1', b'M\xc3\xa9dico'), (b'2', b'Enfermero/a'), (b'3', b'Secretario/a')])),
                ('administrador', models.BooleanField(default=False)),
                ('sexo', models.CharField(max_length=1, choices=[(b'1', b'Masculino'), (b'2', b'Femenino')])),
                ('tlf_cel', models.CharField(max_length=11)),
                ('direccion', models.CharField(max_length=128)),
                ('tlf_casa', models.CharField(max_length=11)),
                ('habilitado', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
