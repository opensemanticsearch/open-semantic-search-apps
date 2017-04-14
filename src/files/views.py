from django.shortcuts import render
from django.shortcuts import render_to_response
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

from etl.tasks import index_file

from models import Files


class FilesForm(ModelForm):

	class Meta:
		model = Files
		fields = '__all__'

class IndexView(generic.ListView):
	model = Files

class DetailView(generic.DetailView):
	model = Files

class CreateView(generic.CreateView):
	model = Files

class UpdateView(generic.UpdateView):
	model = Files


#
# New/additional file
#

def create_file(request):

	if request.method == 'POST':

		form = FilesForm(request.POST, request.FILES)

		if form.is_valid():
			file = form.save()

			return HttpResponseRedirect( reverse('files:detail', args=[file.pk]) ) # Redirect after POST

	else:
		form = FilesForm()

	return render_to_response('files/files_form.html', 
			{'form': form,	}, context_instance=RequestContext(request) )
	

#
# Updated an file
#

def update_file(request, pk):

	file = Files.objects.get(pk=pk)
	
	if request.POST:
		
		form = FilesForm(request.POST, request.FILES, instance=file)
		
		if form.is_valid():
			form.save()

			return HttpResponseRedirect( reverse('files:detail', args=[pk])) # Redirect after POST
		
			pass
	else:
		form = FilesForm(instance=file)

	return render_to_response('files/files_form.html', 
			{'form': form, 'file': file }, context_instance=RequestContext(request) )


#
# Add website to queue
# So a worker will download/read the file and import/download all new articles
#

def crawl(request, pk):

	file = Files.objects.get(pk=pk)
	
	# add to queue
	last_imported = datetime.datetime.now()
	index_file.delay(uri=file.uri)

	# save new timestamp
	file.last_imported = last_imported
	file.save()

	
	return render(request, 'files/files_crawl.html', {'id': pk,})


#
# Add all files to queue where last import was before configured delta time of the file
#

def recrawl(request):

	verbose = True

	log = []
	count = 0
	count_queued = 0

	for file in Files.objects.all():

		count += 1

		if verbose:
			log.append( "Checking delta time of file or directory: {}".format(file) ) 


		add_to_queue = True


		# If delta time, do not import this file within this time by setting add_to_queue to false
		if file.delta and file.last_imported:

			# when next import allowed (because time delta passed)?
			next_import = file.last_imported + timedelta(minutes=file.delta)

			# don't check time delta if last import in future (i.e. if system time was wrong)
			if file.last_imported < timezone.now():			

				# if time for next import not reached, do not index
				if timezone.now() < next_import:
					add_to_queue = False

			if verbose:
				log.append( "Last addition to queue: {}".format(file.last_imported) )
				log.append( "Next addition to queue: {}".format(next_import) ) 


		if add_to_queue:
			
			if verbose:
				log.append( "Adding file or directory to queue: {}".format(file) ) 

			# add to queue
			last_imported = datetime.datetime.now()
			index_file.delay(uri=file.uri)

			# save new timestamp
			file.last_imported = last_imported
			file.save()

			count_queued += 1
	
	#
 	# stats / log
 	#
 	
	response = "Files or directories to queue: {} of {}".format(count_queued, count)

	if len(log) > 0:
		response += "\n\n" + "\n".join(log)
	
	#
	# return response
	#
	
	status = HttpResponse(response)
	status["Content-Type"] = "text/plain" 
	return status
