from django.db import models
from django.core.urlresolvers import reverse

import encodings

class CSV_Manager(models.Model): 

	uri = models.CharField(max_length=1000, blank = True)
	title = models.CharField(max_length=255, blank = True)
	description = models.TextField(blank = True)

	file = models.FileField(upload_to='csv', blank = True)

	# get list of supported encodings for selection
	codecs=[]
	aliases = encodings.aliases.aliases
	for alias in aliases:
		codecs.append(alias)
		codec = aliases[alias]
		codecs.append(codec)

	# dedupe
	codecsunique=[]
	for codec in codecs:
		if not codec in codecsunique:
			codecsunique.append(codec)

	# sort
	codecsunique.sort()
	
	codecschoices=[]
	for codec in codecsunique:
		codecschoices.append( (codec, codec) )


	codec = models.CharField (max_length=255, blank = True, choices=codecschoices,
							help_text = 'Which encoding? (Leave blank for systems default, try modern and international utf-8 or for older german format iso-8859-15)')


	sniff_encoding = models.BooleanField(blank=True, default=True)

	sniff_dialect = models.BooleanField(blank=True, default=False)
	delimiter_is_tab = models.BooleanField(blank = True)
	
	delimiter = models.CharField(max_length=1, blank = True,
								help_text='Leave blank for default , or change to ; or another delimiter char')

	quotechar = models.CharField(max_length=1, blank = True)
	doublequote = models.BooleanField(blank = True)
	escapechar = models.CharField(max_length=1, blank = True)

	title_row = models.IntegerField( blank = True, null = True,
									help_text='Row with column titles. Leave blank if the CSV containes only data and no title row' )
	start_row = models.IntegerField( blank = True, null = True,
									help_text='Row where to start. Leave blank or set to 1 if all rows are data' )

	rows = models.TextField(blank = True)
	rows_include = models.BooleanField(default=False)
	cols = models.TextField(blank = True)
	cols_include = models.BooleanField(default=False)

	def __str__(self):
		return self.uri
	
	def get_absolute_url(self):
		return reverse('csv_manager:detail', kwargs={'pk': self.pk})