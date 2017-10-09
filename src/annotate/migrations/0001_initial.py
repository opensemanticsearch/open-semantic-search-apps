# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesaurus', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('uri', models.CharField(max_length=1000)),
                ('title', models.CharField(max_length=1000, blank=True)),
                ('notes', models.TextField(blank=True)),
                ('tags', models.ManyToManyField(to='thesaurus.Concept', blank=True)),
            ],
        ),
    ]
