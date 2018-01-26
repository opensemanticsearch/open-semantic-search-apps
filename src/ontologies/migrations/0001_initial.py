# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesaurus', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ontologies',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('uri', models.CharField(max_length=16000, blank=True)),
                ('title', models.CharField(max_length=255, blank=True)),
                ('description', models.TextField(blank=True)),
                ('file', models.FileField(upload_to='ontologies', blank=True)),
                ('do_stemming', models.BooleanField(default=True)),
                ('exclude_uri', models.CharField(max_length=16000, blank=True)),
                ('exclude_file', models.FileField(upload_to='uploads', blank=True)),
                ('exclude_text', models.TextField(blank=True)),
                ('facet', models.ForeignKey(to='thesaurus.Facet', null=True, blank=True)),
            ],
        ),
    ]
