# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ontologies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ontologies',
            name='sparql_endpoint',
            field=models.CharField(max_length=16000, blank=True),
        ),
        migrations.AddField(
            model_name='ontologies',
            name='sparql_query',
            field=models.TextField(blank=True),
        ),
    ]
