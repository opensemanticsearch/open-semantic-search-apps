# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesaurus', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='facet',
            name='enabled',
            field=models.NullBooleanField(default=True),
        ),
        migrations.AddField(
            model_name='facet',
            name='facet_limit',
            field=models.IntegerField(null=True, blank=True, default=20),
        ),
        migrations.AddField(
            model_name='facet',
            name='facet_order',
            field=models.IntegerField(null=True, blank=True, default=0),
        ),
        migrations.AddField(
            model_name='facet',
            name='snippets_enabled',
            field=models.NullBooleanField(default=True),
        ),
        migrations.AddField(
            model_name='facet',
            name='snippets_limit',
            field=models.IntegerField(null=True, blank=True, default=10),
        ),
    ]
