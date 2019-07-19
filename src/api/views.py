from django.shortcuts import render

from django.http import HttpResponse

import json

from opensemanticetl.tasks import delete
from opensemanticetl.tasks import enrich
from opensemanticetl.tasks import index_filedirectory
from opensemanticetl.tasks import index_web
from opensemanticetl.tasks import index_rss


#
# add delete task to queue
#

def queue_delete(request):
	uri = request.GET["uri"]

	if 'wait' in request.GET:
		wait = int(request.GET['wait'])
	else:
		wait = 0

	result = delete.apply_async( kwargs={ 'uri': uri }, queue='tasks', priority=6 )
	
	return HttpResponse(json.dumps( {'queue': result.id} ), content_type="application/json")


#
# add data enrichment / plugin processing task to queue
#

def queue_enrich(request):

	uri = request.GET["uri"]

	plugins = request.GET['plugins']

	result = enrich.apply_async( kwargs={ 'plugins': plugins, 'uri': uri }, queue='tasks', priority=5 )
	
	return HttpResponse(json.dumps( {'queue': result.id} ), content_type="application/json")


#
# add file indexing task to queue
#

def queue_index_file(request):

	uri = request.GET["uri"]

	result = index_filedirectory.apply_async( kwargs={ 'filename': uri }, queue='tasks', priority=5 )

	return HttpResponse(json.dumps( {'queue': result.id} ), content_type="application/json")


#
# add web page indexing task to queue
#

def queue_index_web(request):
	uri = request.GET["uri"]

	result = index_web.apply_async( kwargs={ 'uri': uri }, queue='tasks', priority=5 )
	
	return HttpResponse(json.dumps( {'queue': result.id} ), content_type="application/json")


#
# add RSS feed indexing task to queue
#

def queue_index_rss(request):
	uri = request.GET["uri"]

	result = index_rss.apply_async( kwargs={ 'uri': uri }, queue='tasks', priority=5 )
	
	return HttpResponse(json.dumps( {'queue': result.id} ), content_type="application/json")
