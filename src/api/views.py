from django.shortcuts import render

from django.http import HttpResponse

import json

from opensemanticetl.tasks import enrich
from opensemanticetl.tasks import index_file
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

	result = delete.delay(uri=uri)
	
	return HttpResponse(json.dumps( {'queue': result.id} ), content_type="application/json")


#
# add data enrichment / plugin processing task to queue
#

def queue_enrich(request):

	uri = request.GET["uri"]

	plugins = request.GET['plugins']

	if 'wait' in request.GET:
		wait = int(request.GET['wait'])
	else:
		wait = 0

	result = enrich.delay(plugins = plugins, uri=uri, wait = wait )
	
	return HttpResponse(json.dumps( {'queue': result.id} ), content_type="application/json")


#
# add file indexing task to queue
#

def queue_index_file(request):

	uri = request.GET["uri"]

	if 'wait' in request.GET:
		wait = int(request.GET['wait'])
	else:
		wait = 0

	result = index_file.delay(filename=uri, wait = wait )
	
	return HttpResponse(json.dumps( {'queue': result.id} ), content_type="application/json")


#
# add web page indexing task to queue
#

def queue_index_web(request):
	uri = request.GET["uri"]

	if 'wait' in request.GET:
		wait = int(request.GET['wait'])
	else:
		wait = 0

	result = index_web.delay(uri=uri, wait=wait)
	
	return HttpResponse(json.dumps( {'queue': result.id} ), content_type="application/json")


#
# add RSS feed indexing task to queue
#

def queue_index_rss(request):
	uri = request.GET["uri"]

	if 'wait' in request.GET:
		wait = int(request.GET['wait'])
	else:
		wait = 0

	result = index_rss.delay(uri=uri, wait=wait)
	
	return HttpResponse(json.dumps( {'queue': result.id} ), content_type="application/json")
