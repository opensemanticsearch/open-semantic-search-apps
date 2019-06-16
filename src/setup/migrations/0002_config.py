# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
	('setup', '0001_initial'),
    ]

    operations = [
	migrations.RunSQL("INSERT INTO setup_setup (id,title,description,language,languages,languages_force,ocr_languages,ocr,ocr_pdf,ocr_descew,ner_spacy,ner_stanford) VALUES (1,'default','Default config','en','en,de,fr,hu,it,pt,nl,cz,ro,ru,ar,fa','en','eng',1,1,0,1,0);"),
    ]
