from django.db import models
from django.core.urlresolvers import reverse

# Types of queries
query_type_chooices = (
						('PHRASE', 'Phrase (exact match of the complete search query)'),
						('AND', 'AND (All words of query in document)'),
						('OR', 'OR (Some words of the query in document)'),
						('RAW', 'Raw query (Apache lucene standard)'),
						)

# Facet / field / property
class Facet(models.Model):
	
	label = models.CharField(max_length=255)
	facet = models.CharField(max_length=255)
	enabled = models.NullBooleanField(default=True, null=True, blank=True)
	closed = models.NullBooleanField(default=False, null=True, blank=True)
	facet_limit = models.IntegerField(default=20, null=True, blank=True)
	snippets_enabled = models.NullBooleanField(default=True, null=True, blank=True)
	snippets_limit = models.IntegerField(default=10, null=True, blank=True)
	graph_enabled = models.NullBooleanField(default=True, null=True, blank=True)
	graph_limit = models.IntegerField(default=50, null=True, blank=True)
	facet_order = models.IntegerField(default=0, null=True, blank=True)

	style_color = models.CharField(max_length=20, blank=True, default = 'black')
	style_color_background = models.CharField(max_length=20, blank=True, default = 'lightgray')

	uri = models.CharField(max_length=1000, blank=True)
	
	def __str__(self):
		
		name = self.label
		if not name:
			name = self.facet
		
		return name


class Group(models.Model):
	
	parent = models.ForeignKey('Group', blank=True, null=True)
	
	prefLabel = models.CharField(max_length=1000, blank=True)
	
	facet = models.ForeignKey(Facet, blank=True, null=True)
	
	def __str__(self):
		return self.title
	
	def tags(self):
		return GroupTag.objects.filter(group=self)



class GroupTag(models.Model):
	group = models.ForeignKey(Group)
	facet = models.ForeignKey(Facet, null=True)
	prefLabel = models.CharField(max_length=1000, blank=True)
	
	def __str__(self):
		return self.facet.label + ': ' + self.prefLabel


# Concept or Entity
class Concept(models.Model):
	
	uri = models.CharField(max_length=1000, blank=True)
	
	prefLabel = models.CharField(max_length=1000, blank=True)
	lang = models.CharField(max_length=3, blank=True)
	
	note = models.TextField(blank = True)
	definition = models.TextField(blank = True)
	example = models.TextField(blank = True)
	
	query = models.CharField(max_length=1000, blank=True)
	
	query_type = models.CharField(max_length=6,
                                      choices=query_type_chooices,
                                      default='PHRASE')
	
	facet = models.ForeignKey(Facet, blank=True, null=True)
	
	groups = models.ManyToManyField(Group, blank=True, null=True)
	
	delta = models.IntegerField(default=0, null=True, blank=True)
	last_run = models.DateTimeField(null=True, blank=True)
	
	def __str__(self):
		
		name = self.prefLabel
		
		if not name:
			name = self.query
		
		if not name:
			name = self.id
		
		return name
	
	def alternates(self):
		return Alternate.objects.filter(concept=self)
	
	def hiddens(self):
		return Hidden.objects.filter(concept=self)
	
	def broader(self):
		return Broader.objects.filter(concept=self)
	
	def narrower(self):
		return Narrower.objects.filter(concept=self)
	
	def related(self):
		return Related.objects.filter(concept=self)
	
	def tags(self):
		return ConceptTag.objects.filter(concept=self)
	
	def get_absolute_url(self):
		return reverse( 'thesaurus:detail', kwargs={'pk': self.pk} )


#
# SKOS:altLabel
#


# The skos:altLabel property to assign alternative lexical label(s) to a concept.
# This is helpful when assigning labels beyond the one that is preferred for the concept,
# for instance when synonyms need to be represented

# Source: https://www.w3.org/TR/skos-primer/#secalt

class Alternate(models.Model): 

	concept = models.ForeignKey(Concept)

	altLabel = models.CharField(max_length=1000, blank=True)
	lang = models.CharField(max_length=3, blank=True)
	
	query = models.CharField(max_length=1000, blank=True)
	query_type = models.CharField(max_length=6,
                                      choices=query_type_chooices,
                                      default='PHRASE')

	def __str__(self):
		return self.altLabel

#
# SKOS:hiddenLabel
#

# A hidden lexical label, represented by means of the skos:hiddenLabel property, is a lexical label for a resource, where a KOS designer would like that character string to be accessible to applications performing text-based indexing and search operations, but would not like that label to be visible otherwise. Hidden labels may for instance be used to include misspelled variants of other lexical labels. 
# Source: https://www.w3.org/TR/skos-primer/#sechidden

class Hidden(models.Model): 

	concept = models.ForeignKey(Concept)

	hiddenLabel = models.CharField(max_length=1000, blank=True)
	lang = models.CharField(max_length=3, blank=True)
	
	query = models.CharField(max_length=1000, blank=True)
	query_type = models.CharField(max_length=6,
                                      choices=query_type_chooices,
                                      default='PHRASE')


class Exclude(models.Model): 

	concept = models.ForeignKey(Concept)

	label = models.CharField(max_length=1000, blank=True)
	lang = models.CharField(max_length=3, blank=True)
	
	query = models.CharField(max_length=1000, blank=True)
	query_type = models.CharField(max_length=6,
                                      choices=query_type_chooices,
                                      default='PHRASE')

	def __str__(self):
		
		name = self.title
		
		if not name:
			name = self.query

		if not name:
			name = self.id
	
		return name


class ConceptTag(models.Model):
	concept = models.ForeignKey(Concept)

	label = models.CharField(max_length=1000, blank=True)
	
	facet = models.ForeignKey(Facet, blank=True, null=True)
	
	def __str__(self):
		return self.label
		

class Broader(models.Model):
	concept = models.ForeignKey(Concept)
	broader = models.ForeignKey(Concept, related_name="concept_broader", blank=True, null=True)


class Narrower(models.Model):
	concept = models.ForeignKey(Concept)
	narrower = models.ForeignKey(Concept, related_name="concept_narrower", blank=True, null=True)


class Related(models.Model):
	concept = models.ForeignKey(Concept)
	related = models.ForeignKey(Concept, related_name="concept_related", blank=True, null=True)
