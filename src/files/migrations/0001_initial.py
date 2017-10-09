# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Files',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uri', models.CharField(max_length=1000)),
                ('delta', models.IntegerField(default=1440)),
                ('title', models.CharField(max_length=1000, blank=True)),
                ('description', models.TextField(blank=True)),
                ('last_imported', models.DateTimeField(null=True, blank=True)),
            ],
        ),
    ]
