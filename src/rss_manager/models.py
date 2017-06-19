from django.db import models



class RSS_Feed(models.Model):

	uri = models.CharField(max_length=1000, blank=False)

	delta = models.IntegerField(default=60)
	
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
