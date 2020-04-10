# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
	('thesaurus', '0012_iban'),
    ]

    operations = [
	migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,style_color,style_color_background,uri,enabled,facet_limit,snippets_enabled,snippets_limit,graph_enabled,facet_order) VALUES ('law_clause_ss','Law clause','black','cyan','', 1, 10, 1, 10, 1, 17);"),
	migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,style_color,style_color_background,uri,enabled,facet_limit,snippets_enabled,snippets_limit,graph_enabled,facet_order) VALUES ('law_code_ss','Law code','black','cyan','', 1, 10, 1, 10, 1, 17);"),
	migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,style_color,style_color_background,uri,enabled,facet_limit,snippets_enabled,snippets_limit,graph_enabled,facet_order) VALUES ('law_code_clause_ss','Law code clause','black','cyan','', 1, 10, 1, 10, 1, 17);"),
    ]
