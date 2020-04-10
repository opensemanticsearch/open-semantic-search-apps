# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
	('ontologies', '0003_auto_20181031_1422'),
	('thesaurus', '0013_law'),
    ]

    operations = [
	migrations.RunSQL("INSERT INTO ontologies_ontologies (facet_id, title, file, uri, sparql_endpoint, sparql_query, description, exclude_uri, exclude_file, exclude_text, stemming, stemming_force, stemming_hunspell, stemming_force_hunspell) VALUES ((SELECT id from thesaurus_facet where facet='law_code_ss'), 'Law codes','ontologies/law_codes.rdf', '', '', '', 'Export of law code ids and labels from Wikidata', '', '', '', '', '', '', '');"),
    ]
