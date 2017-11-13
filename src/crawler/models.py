from django.db import models


# Types of crawlers
crawler_type_chooices = (
						('PAGE', 'Index only this web page'),
						('PATH', 'Crawl all web pages within this path'),
						('DOMAIN', 'Crawl full domain and subdomains'),
			)


class Crawler(models.Model):

	uri = models.CharField(max_length=1000, blank=False)

	crawler_type = models.CharField(max_length=6,
                                      choices=crawler_type_chooices,
                                      default='PATH')
	
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
