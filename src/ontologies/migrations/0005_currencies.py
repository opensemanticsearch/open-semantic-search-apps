# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ontologies', '0004_law_codes'),
        ('thesaurus', '0015_currency'),
    ]

    operations = [
        migrations.RunSQL("INSERT INTO ontologies_ontologies (facet_id, title, file, uri, sparql_endpoint, sparql_query, description, exclude_uri, exclude_file, exclude_text, stemming, stemming_force, stemming_hunspell, stemming_force_hunspell) VALUES ((SELECT id from thesaurus_facet where facet='currency_ss'), 'Currencies','ontologies/currencies.rdf', '', '', '', 'Export of currencies from Wikidata', '', '', '', '', '', '', '');"),
    ]
