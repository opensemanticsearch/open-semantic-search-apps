# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Hypothesis',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(blank=True, max_length=1000)),
                ('description', models.TextField(blank=True)),
                ('api', models.CharField(max_length=1000)),
                ('last_imported', models.DateTimeField(blank=True, null=True)),
                ('last_update', models.CharField(blank=True, max_length=1000)),
                ('delta', models.IntegerField(default=10)),
                ('uri', models.CharField(blank=True, max_length=1000)),
                ('user', models.CharField(blank=True, max_length=1000)),
                ('group', models.CharField(blank=True, max_length=1000)),
                ('tag', models.CharField(blank=True, max_length=1000)),
            ],
        ),
    ]
