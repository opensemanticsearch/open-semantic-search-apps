from django.db import models

class Setup(models.Model):

	title = models.CharField(max_length=1000, blank=True)
	description = models.TextField(blank=True)

	language = models.CharField(max_length=2, default="en", blank=True)

	languages = models.CharField(max_length=300, default="en", blank=True)
	languages_force = models.CharField(max_length=300, default="en", blank=True)

	languages_hunspell = models.CharField(max_length=300, default="hu", blank=True)
	languages_force_hunspell = models.CharField(max_length=300, default="", blank=True)
	
	ocr = models.BooleanField(default=True)
	ocr_later = models.BooleanField(default=True)

	ocr_languages = models.CharField(max_length=300, default="eng", blank=True)

	ocr_descew = models.BooleanField(default=False)

	ocr_pdf = models.BooleanField(default=True)
	
	ner_spacy = models.BooleanField(default=True)

	ner_stanford = models.BooleanField(default=False)

	segmentation_pages = models.BooleanField(default=False)
	segmentation_pages_preview = models.BooleanField(default=False)

	segmentation_sentences = models.BooleanField(default=False)

	graph_neo4j = models.BooleanField(default=False)
	graph_neo4j_host = models.CharField(max_length=1000, blank=True)
	graph_neo4j_user = models.CharField(max_length=1000, blank=True)
	graph_neo4j_password = models.CharField(max_length=1000, blank=True)
	graph_neo4j_browser = models.CharField(max_length=1000, blank=True)

	url_tasks = models.CharField(max_length=1000, blank=True, default="http://localhost:5555/tasks")
