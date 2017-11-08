from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template import RequestContext
from django.views import generic
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone

import datetime
from datetime import timedelta

from hypothesis.models import Hypothesis

import opensemanticetl.etl_hypothesis

class HypothesisForm(ModelForm):

	class Meta:
		model = Hypothesis
		#fields = '__all__'
		exclude = ['api']

class IndexView(generic.ListView):
	model = Hypothesis

class DetailView(generic.DetailView):
	model = Hypothesis

class CreateView(generic.CreateView):
	model = Hypothesis

class UpdateView(generic.UpdateView):
	model = Hypothesis


#
# New/additional import
#

def create_hypothesis(request):

	if request.method == 'POST':

		form = HypothesisForm(request.POST, request.FILES)

		if form.is_valid():
			hypothesis = form.save()

			return HttpResponseRedirect( reverse('hypothesis:detail', args=[hypothesis.pk]) ) # Redirect after POST

	else:
		form = HypothesisForm()

	return render(request, 'hypothesis/hypothesis_form.html', 
			{'form': form,	} )
	

#
# Update
#

def update_hypothesis(request, pk):

	hypothesis = Hypothesis.objects.get(pk=pk)
	
	if request.POST:
		
		form = HypothesisForm(request.POST, request.FILES, instance=hypothesis)
		
		if form.is_valid():
			form.save()

			return HttpResponseRedirect( reverse('hypothesis:detail', args=[pk])) # Redirect after POST
		
			pass
	else:
		form = HypothesisForm(instance=hypothesis)

	return render(request, 'hypothesis/hypothesis_form.html', 
			{'form': form, 'hypothesis': hypothesis } )

#
# ETL - import annotations from Hypothesis
#

def etl_hypothesis(pk):

	last_imported = datetime.datetime.now()

	hypothesis = Hypothesis.objects.get(pk=pk)

	last_update = hypothesis.last_update


	limit = 200
	api =  'https://hypothes.is/api'

	if hypothesis.api:
	    api = hypothesis.api

	searchurl = '{}/search?limit={}&sort=updated&order=desc'.format(api, limit)

	if hypothesis.user:
		searchurl += "&user={}".format(hypothesis.user)

	if hypothesis.group:
		searchurl += "&group={}".format(hypothesis.group)

	if hypothesis.tag:
		searchurl += "&tag={}".format(hypothesis.tag)

	if hypothesis.uri:
		searchurl += "&uri={}".format(hypothesis.uri)

	# run import
	last_update = opensemanticetl.etl_hypothesis.etl_hypothesis_annotations(searchurl, last_update=hypothesis.last_update)

	# new timestamp of last downloaded annotation
	hypothesis.last_update = last_update

	# new timestamp of last API search
	hypothesis.last_imported = last_imported

	hypothesis.save()


def crawl(request, pk):

	etl_hypothesis(pk)

	return render(request, 'hypothesis/hypothesis_crawl.html', {'id': pk,})


#
# Do imports where last import was before configured delta time
#

def recrawl(request):

	verbose = True

	log = []
	count = 0
	count_queued = 0

	for hypothesis in Hypothesis.objects.all():

		count += 1

		if verbose:
			log.append( "Checking delta time for Hypothesis import: {}".format(hypothesis) ) 


		do_import = True

		# If delta time 0 no automatic import
		if not hypothesis.delta:
			do_import = False

		# If delta time, do not import within this time by setting add_to_queue to false
		if hypothesis.delta and hypothesis.last_imported:

			# when next import allowed (because time delta passed)?
			next_import = hypothesis.last_imported + timedelta(minutes=hypothesis.delta)

			# don't check time delta if last import in future (i.e. if system time was wrong)
			if hypothesis.last_imported < timezone.now():

				# if time for next import not reached, do not index
				if timezone.now() < next_import:
					do_import = False

			if verbose:
				log.append( "Last import: {}".format(hypothesis.last_imported) )
				log.append( "Next import: {}".format(next_import) ) 


		if do_import:

			if verbose:
				log.append( "Hypothesis API call: {}".format(hypothesis) ) 
			
			etl_hypothesis(pk=hypothesis.pk)

			count_queued += 1
	
	#
 	# stats / log
 	#
 	
	response = "Hypothesis API calls: {} of {}".format(count_queued, count)

	if len(log) > 0:
		response += "\n\n" + "\n".join(log)
	
	#
	# return response
	#
	
	status = HttpResponse(response)
	status["Content-Type"] = "text/plain" 
	return status
