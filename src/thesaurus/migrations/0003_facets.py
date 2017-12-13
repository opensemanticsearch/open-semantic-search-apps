# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
	('thesaurus', '0001_initial'),
	('thesaurus', '0002_facet_fields'),
    ]

    operations = [
	migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,uri,enabled,facet_limit,snippets_enabled,snippets_limit,facet_order) VALUES ('tag_ss','Tags','dc:subject', 1, 10, 1, 10, 2);"),
	migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,uri,enabled,facet_limit,snippets_enabled,snippets_limit,facet_order) VALUES ('language_s','Language','', 1, 10, 0, 10, 10);"),
	migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,uri,enabled,facet_limit,snippets_enabled,snippets_limit,facet_order) VALUES ('author_s','Author','', 1, 10, 1, 10, 1);"),
	migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,uri,enabled,facet_limit,snippets_enabled,snippets_limit,facet_order) VALUES ('person_ss','Persons','', 1, 10, 1, 10, 3);"),
	migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,uri,enabled,facet_limit,snippets_enabled,snippets_limit,facet_order) VALUES ('organization_ss','Organizations','', 1, 10, 1, 10, 4);"),
	migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,uri,enabled,facet_limit,snippets_enabled,snippets_limit,facet_order) VALUES ('location_ss','Location','', 1, 10, 1, 10, 5);"),
	migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,uri,enabled,facet_limit,snippets_enabled,snippets_limit,facet_order) VALUES ('email_ss','Email','', 1, 10, 1, 10, 10);"),
	migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,uri,enabled,facet_limit,snippets_enabled,snippets_limit,facet_order) VALUES ('message_from_ss','Message from','', 1, 10, 1, 10, 11);"),
	migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,uri,enabled,facet_limit,snippets_enabled,snippets_limit,facet_order) VALUES ('message_to_ss','Message to','', 1, 10, 1, 10, 12);"),
	migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,uri,enabled,facet_limit,snippets_enabled,snippets_limit,facet_order) VALUES ('message_cc_ss','Message CC','', 1, 10, 1, 10, 13);"),
	migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,uri,enabled,facet_limit,snippets_enabled,snippets_limit,facet_order) VALUES ('message_bcc_ss','Message BCC','', 1, 10, 1, 10, 14);"),
	migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,uri,enabled,facet_limit,snippets_enabled,snippets_limit,facet_order) VALUES ('content_type_group','Content type group','', 1, 10, 0, 10, 20);"),
	migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,uri,enabled,facet_limit,snippets_enabled,snippets_limit,facet_order) VALUES ('content_type','Content type','', 1, 10, 0, 10, 21);"),
	migrations.RunSQL("INSERT INTO thesaurus_facet (facet,label,uri,enabled,facet_limit,snippets_enabled,snippets_limit,facet_order) VALUES ('hashtag_ss','Hashtags','dc:subject', 1, 10, 1, 10, 15);"),
    ]
