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

from opensemanticetl.etl_hypothesis import Connector_Hypothesis 

class HypothesisForm(ModelForm):

	class Meta:
		model = Hypothesis
		fields = '__all__'

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

	hypothesis = Hypothesis.objects.get(pk=pk)

	connector = Connector_Hypothesis()
	
	# authorization
	if hypothesis.api:
	    connector.api = hypothesis.api

	if hypothesis.token:
	    connector.token = hypothesis.token

	# start time
	last_imported = datetime.datetime.now()

	# run import
	last_update = connector.etl_annotations(last_update=hypothesis.last_update, user=hypothesis.user, group=hypothesis.group, tag=hypothesis.tag, uri=hypothesis.uri)

	# new timestamp of last imported annotation
	hypothesis.last_update = last_update

	# set new timestamp of last import / call of search API to start time
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
