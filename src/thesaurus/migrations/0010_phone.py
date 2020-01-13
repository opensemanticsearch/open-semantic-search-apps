# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
	('thesaurus', '0009_facet_closed'),
    ]

    operations = [
	migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,style_color,style_color_background,uri,enabled,facet_limit,snippets_enabled,snippets_limit,graph_enabled,facet_order) VALUES ('phone_ss','Phone number(s)','black','cyan','https://schema.org/telephone', 1, 10, 1, 10, 0, 9);"),

    ]
