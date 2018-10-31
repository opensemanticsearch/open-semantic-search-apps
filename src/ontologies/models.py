from django.db import models
from django.core.urlresolvers import reverse

import os.path

from thesaurus.models import Facet



class Ontologies(models.Model): 

	uri = models.CharField(max_length=16000, blank = True)
	title = models.CharField(max_length=255, blank = True)
	description = models.TextField(blank = True)

	file = models.FileField(upload_to='ontologies', blank = True)

	facet = models.ForeignKey(Facet, blank=True, null=True)

	sparql_endpoint = models.CharField(max_length=16000, blank = True)

	sparql_query = models.TextField(blank = True)

	stemming = models.CharField(max_length=300, default="en", blank=True)
	stemming_force = models.CharField(max_length=300, default="", blank=True)

	stemming_hunspell = models.CharField(max_length=300, default="", blank=True)
	stemming_force_hunspell = models.CharField(max_length=300, default="", blank=True)

	exclude_uri = models.CharField(max_length=16000, blank = True)
	exclude_file = models.FileField(upload_to='uploads', blank = True)
	exclude_text = models.TextField(blank = True)


	# todo:
	# - rdf/owl/skos: de/select label languages
	# - exclude entries
	# - tables (which columns of excel list or ?
	# - stemming

	def __str__(self):

		if self.title:
			label=self.title
		elif self.uri:
			label=self.uri
		elif self.file:
			label = os.path.basename( self.file.name )
		else:
			label=str(self.id)

		return label
	
	def get_absolute_url(self):
		return reverse('ontologies:detail', kwargs={'pk': self.pk})