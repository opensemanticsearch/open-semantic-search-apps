# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
	('thesaurus', '0001_initial'),
	('thesaurus', '0002_facet_fields'),
	('thesaurus', '0003_facets'),
    ]

    operations = [
	migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,uri,enabled,facet_limit,snippets_enabled,snippets_limit,facet_order) VALUES ('money_ss','Money','http://schema.org/MonetaryAmount', 1, 10, 1, 10, 17);"),
    ]
