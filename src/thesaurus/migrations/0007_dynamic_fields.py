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
	('thesaurus', '0006_authors'),
    ]

    operations = [
	migrations.RunSQL("UPDATE thesaurus_facet SET facet='content_type_ss' WHERE facet='content_type'"),
	migrations.RunSQL("UPDATE thesaurus_facet SET facet='content_type_group_ss' WHERE facet='content_type_group'"),
	migrations.RunSQL("UPDATE thesaurus_facet SET facet='Message-From_ss' WHERE facet='message_from_ss'"),
	migrations.RunSQL("UPDATE thesaurus_facet SET facet='Message-To_ss' WHERE facet='message_to_ss'"),
	migrations.RunSQL("UPDATE thesaurus_facet SET facet='Message-CC_ss' WHERE facet='message_cc_ss'"),
	migrations.RunSQL("UPDATE thesaurus_facet SET facet='Message-BCC_ss' WHERE facet='message_bcc_ss'"),
    ]
