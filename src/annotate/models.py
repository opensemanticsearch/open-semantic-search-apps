from django.db import models
from django.core.urlresolvers import reverse

from thesaurus.models import Concept


class Annotation(models.Model):

	uri = models.CharField(max_length=1000)

	title = models.CharField(max_length=1000, blank=True)

	notes = models.TextField(blank = True)

	tags = models.ManyToManyField(Concept, blank=True)

	def __str__(self):
		
		name = self.uri
		
		if not name:
			name = self.query

		if not name:
			name = self.id
	
		return name

	def get_absolute_url(self):
		return reverse('annotate:detail', kwargs={'pk': self.pk})
