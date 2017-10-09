# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Crawler',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('uri', models.CharField(max_length=1000)),
                ('sitemap', models.CharField(null=True, blank=True, max_length=1000)),
                ('delta', models.IntegerField(default=1440)),
                ('title', models.CharField(blank=True, max_length=1000)),
                ('description', models.TextField(blank=True)),
                ('last_imported', models.DateTimeField(null=True, blank=True)),
            ],
        ),
    ]
