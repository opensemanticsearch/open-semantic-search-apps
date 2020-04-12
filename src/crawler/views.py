from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template import RequestContext
from django.views import generic
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import redirect


import datetime
from datetime import timedelta

from crawler.models import Crawler


class CrawlerForm(ModelForm):

	class Meta:
		model = Crawler
		fields = '__all__'

class IndexView(generic.ListView):
	model = Crawler

class DetailView(generic.DetailView):
	model = Crawler

class CreateView(generic.CreateView):
	model = Crawler

class UpdateView(generic.UpdateView):
	model = Crawler


#
# New/additional crawler
#

def create_crawler(request):

	if request.method == 'POST':

		form = CrawlerForm(request.POST, request.FILES)

		if form.is_valid():
			crawler = form.save()

			return HttpResponseRedirect( reverse('crawler:detail', args=[crawler.pk]) ) # Redirect after POST

	else:
		form = CrawlerForm()

	return render(request, 'crawler/crawler_form.html', 
			{'form': form,	} )
	

#
# Updated an crawler
#

def update_crawler(request, pk):

	crawler = Crawler.objects.get(pk=pk)
	
	if request.POST:
		
		form = CrawlerForm(request.POST, request.FILES, instance=crawler)
		
		if form.is_valid():
			form.save()

			return HttpResponseRedirect( reverse('crawler:detail', args=[pk])) # Redirect after POST
		
			pass
	else:
		form = CrawlerForm(instance=crawler)

	return render(request, 'crawler/crawler_form.html', 
			{'form': form, 'crawler': crawler } )


def etl(pk):

	last_imported = datetime.datetime.now()

	crawler = Crawler.objects.get(pk=pk)
	
	# add to queue
	if crawler.sitemap:
		# get sitemap and add urls to queue
		from opensemanticetl.tasks import index_sitemap
		index_sitemap.apply_async( kwargs={ 'uri': crawler.sitemap }, queue='open_semantic_etl_tasks', priority=5 )
		
	else:
		if crawler.crawler_type=="DOMAIN" or crawler.crawler_type=="PATH":
			# add website to queue
			from opensemanticetl.tasks import index_web_crawl
			index_web_crawl.apply_async( kwargs={ 'uri': crawler.uri, 'crawler_type': crawler.crawler_type }, queue='open_semantic_etl_tasks', priority=5 )
		else:
			# add web page to queue
			from opensemanticetl.tasks import index_web
			index_web.apply_async( kwargs={ 'uri': crawler.uri }, queue='open_semantic_etl_tasks', priority=5 )

	# save new timestamp
	crawler.last_imported = last_imported
	crawler.save()

#
# Delete entry
#

def delete(request, pk):

	crawler = Crawler.objects.get(pk=pk)
	
	crawler.delete()

	return redirect('crawler:index')


#
# Add website to queue
# So a worker will download/read the website and import/download all new articles
#

def crawl(request, pk):

	etl(pk)

	return render(request, 'crawler/crawler_crawl.html', {'id': pk,})


#
# Add all websites to queue where last import was before configured delta time of the website
#

def recrawl(request):

	verbose = True

	log = []
	count = 0
	count_queued = 0

	for crawler in Crawler.objects.all():

		count += 1

		if verbose:
			log.append( "Checking delta time of website: {}".format(crawler) ) 


		add_to_queue = True

		# If delta 0, no automatic import
		if not crawler.delta:
			add_to_queue = False

		# If delta time, do not import this website within this time by setting add_to_queue to false
		if crawler.delta and crawler.last_imported:

			# when next import allowed (because time delta passed)?
			next_import = crawler.last_imported + timedelta(minutes=crawler.delta)

			# don't check time delta if last import in future (i.e. if system time was wrong)
			if crawler.last_imported < timezone.now():			

				# if time for next import not reached, do not index
				if timezone.now() < next_import:
					add_to_queue = False

			if verbose:
				log.append( "Last addition to queue: {}".format(crawler.last_imported) )
				log.append( "Next addition to queue: {}".format(next_import) ) 


		if add_to_queue:

			if verbose:
				log.append( "Adding website to queue: {}".format(crawler) ) 
			
			etl(crawler.pk)

			count_queued += 1
	
	#
 	# stats / log
 	#
 	
	response = "Websites to queue: {} of {}".format(count_queued, count)

	if len(log) > 0:
		response += "\n\n" + "\n".join(log)
	
	#
	# return response
	#
	
	status = HttpResponse(response)
	status["Content-Type"] = "text/plain" 
	return status
