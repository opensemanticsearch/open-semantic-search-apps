from django.db import models


class Hypothesis(models.Model):

	title = models.CharField(max_length=1000, blank=True)
	description = models.TextField(blank=True)

	api = models.CharField(max_length=1000, blank=True)
	token = models.CharField(max_length=1000, blank=True)
	
	last_imported = models.DateTimeField(null=True, blank=True)

	last_update = models.CharField(max_length=1000, blank=True)
	delta = models.IntegerField(default=15)
	
	uri = models.CharField(max_length=1000, blank=True)
	user = models.CharField(max_length=1000, blank=True, default='opensemanticsearch')
	group = models.CharField(max_length=1000, blank=True)
	tag = models.CharField(max_length=1000, blank=True)

	def __str__(self):
		
		title = self.title
		
		if not title:
			title = self.uri

		if not title:
			title = self.user

		if not title:
			title = self.group

		if not title:
			title = self.tag

		if not title:
			title = self.id
	
		return title
