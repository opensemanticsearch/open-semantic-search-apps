# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Alternate',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('altLabel', models.CharField(blank=True, max_length=1000)),
                ('lang', models.CharField(blank=True, max_length=3)),
                ('query', models.CharField(blank=True, max_length=1000)),
                ('query_type', models.CharField(max_length=6, choices=[('PHRASE', 'Phrase (exact match of the complete search query)'), ('AND', 'AND (All words of query in document)'), ('OR', 'OR (Some words of the query in document)'), ('RAW', 'Raw query (Apache lucene standard)')], default='PHRASE')),
            ],
        ),
        migrations.CreateModel(
            name='Broader',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('uri', models.CharField(blank=True, max_length=1000)),
                ('prefLabel', models.CharField(blank=True, max_length=1000)),
                ('lang', models.CharField(blank=True, max_length=3)),
                ('note', models.TextField(blank=True)),
                ('definition', models.TextField(blank=True)),
                ('example', models.TextField(blank=True)),
                ('query', models.CharField(blank=True, max_length=1000)),
                ('query_type', models.CharField(max_length=6, choices=[('PHRASE', 'Phrase (exact match of the complete search query)'), ('AND', 'AND (All words of query in document)'), ('OR', 'OR (Some words of the query in document)'), ('RAW', 'Raw query (Apache lucene standard)')], default='PHRASE')),
                ('delta', models.IntegerField(blank=True, null=True, default=0)),
                ('last_run', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ConceptTag',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('label', models.CharField(blank=True, max_length=1000)),
                ('concept', models.ForeignKey(to='thesaurus.Concept')),
            ],
        ),
        migrations.CreateModel(
            name='Exclude',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('label', models.CharField(blank=True, max_length=1000)),
                ('lang', models.CharField(blank=True, max_length=3)),
                ('query', models.CharField(blank=True, max_length=1000)),
                ('query_type', models.CharField(max_length=6, choices=[('PHRASE', 'Phrase (exact match of the complete search query)'), ('AND', 'AND (All words of query in document)'), ('OR', 'OR (Some words of the query in document)'), ('RAW', 'Raw query (Apache lucene standard)')], default='PHRASE')),
                ('concept', models.ForeignKey(to='thesaurus.Concept')),
            ],
        ),
        migrations.CreateModel(
            name='Facet',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('uri', models.CharField(blank=True, max_length=1000)),
                ('label', models.CharField(max_length=255)),
                ('facet', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('prefLabel', models.CharField(blank=True, max_length=1000)),
                ('facet', models.ForeignKey(null=True, blank=True, to='thesaurus.Facet')),
                ('parent', models.ForeignKey(null=True, blank=True, to='thesaurus.Group')),
            ],
        ),
        migrations.CreateModel(
            name='GroupTag',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('prefLabel', models.CharField(blank=True, max_length=1000)),
                ('facet', models.ForeignKey(to='thesaurus.Facet', null=True)),
                ('group', models.ForeignKey(to='thesaurus.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Hidden',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('hiddenLabel', models.CharField(blank=True, max_length=1000)),
                ('lang', models.CharField(blank=True, max_length=3)),
                ('query', models.CharField(blank=True, max_length=1000)),
                ('query_type', models.CharField(max_length=6, choices=[('PHRASE', 'Phrase (exact match of the complete search query)'), ('AND', 'AND (All words of query in document)'), ('OR', 'OR (Some words of the query in document)'), ('RAW', 'Raw query (Apache lucene standard)')], default='PHRASE')),
                ('concept', models.ForeignKey(to='thesaurus.Concept')),
            ],
        ),
        migrations.CreateModel(
            name='Narrower',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('concept', models.ForeignKey(to='thesaurus.Concept')),
                ('narrower', models.ForeignKey(null=True, blank=True, related_name='concept_narrower', to='thesaurus.Concept')),
            ],
        ),
        migrations.CreateModel(
            name='Related',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('concept', models.ForeignKey(to='thesaurus.Concept')),
                ('related', models.ForeignKey(null=True, blank=True, related_name='concept_related', to='thesaurus.Concept')),
            ],
        ),
        migrations.AddField(
            model_name='concepttag',
            name='facet',
            field=models.ForeignKey(null=True, blank=True, to='thesaurus.Facet'),
        ),
        migrations.AddField(
            model_name='concept',
            name='facet',
            field=models.ForeignKey(null=True, blank=True, to='thesaurus.Facet'),
        ),
        migrations.AddField(
            model_name='concept',
            name='groups',
            field=models.ManyToManyField(blank=True, to='thesaurus.Group', null=True),
        ),
        migrations.AddField(
            model_name='broader',
            name='broader',
            field=models.ForeignKey(null=True, blank=True, related_name='concept_broader', to='thesaurus.Concept'),
        ),
        migrations.AddField(
            model_name='broader',
            name='concept',
            field=models.ForeignKey(to='thesaurus.Concept'),
        ),
        migrations.AddField(
            model_name='alternate',
            name='concept',
            field=models.ForeignKey(to='thesaurus.Concept'),
        ),
    ]
