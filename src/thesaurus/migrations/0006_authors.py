# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
	('thesaurus', '0001_initial'),
	('thesaurus', '0002_facet_fields'),
	('thesaurus', '0003_facets'),
	('thesaurus', '0004_money'),
	('thesaurus', '0005_hypothesis'),
    ]

    operations = [
	migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,uri,enabled,facet_limit,snippets_enabled,snippets_limit,facet_order) VALUES ('author_ss','Author(s)','http://schema.org/Author', 1, 10, 1, 10, 1);"),
    ]
