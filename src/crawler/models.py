from django.db import models



class Crawler(models.Model):

	uri = models.CharField(max_length=1000, blank=False)

	sitemap = models.CharField(max_length=1000, null=True, blank=True)

	delta = models.IntegerField(default=1440)
	
	title = models.CharField(max_length=1000, blank=True)

	description = models.TextField(blank=True)
	
	last_imported = models.DateTimeField(null=True, blank=True)
	


	def __str__(self):
		
		name = self.title
		
		if not name:
			name = self.uri

		if not name:
			name = self.id
	
		return name
