# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesaurus', '0014_filename_extension'),
    ]

    operations = [
        migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,style_color,style_color_background,uri,enabled,facet_limit,snippets_enabled,snippets_limit,graph_enabled,facet_order) VALUES ('currency_ss','Currency','black','cyan','https://schema.org/currency', 1, 10, 1, 10, 0, 18);"),
    ]
