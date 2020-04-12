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
from django import forms

import datetime
from datetime import timedelta


from files.models import Files
from setup.models import Setup


# Language of UI
PRIORITY_CHOICES = (
	(39, 'A++: Highest top priority (process before all other queues)'),
	(37, 'A+: Higher priority (processed before queues A, B, C and D)'),
	(35, 'A: High priority (processed before standard queues B, C and D)'),
	(22, 'B: Normal (per default priorized queue for text extraction tasks for PDFs and office documents)'),
	(20, 'C: Lower (queue for text extraction tasks of other file formats)'),
)

PRIORITY_OCR_CHOICES = (
	(38, 'A++: Highest top priority (process before all other queues)'),
	(36, 'A+: Higher priority (processed before queues A, B, C and D)'),
	(34, 'A: High priority (processed before standard queues B, C and D)'),
	(21, 'B: Normal (per default priorized queue for text extraction tasks for PDFs and office documents)'),
	(20, 'C: Lower (queue for text extraction tasks of other file formats)'),
	(0, 'D: Lowest (queues for OCR tasks, so runned after plain text from all documents yet extracted and searchable)'),
)

PRIORITY_TO_OCR_PRIORITY = {
	39: 19,
	37: 18,
	35: 17,
	22: 5,
	20: 4,
}

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


class PrioritizeForm(forms.Form):
		
	filename = forms.CharField(widget=forms.TextInput, required=True)

	priority = forms.IntegerField(
		required=True,
		initial=35,
		widget=forms.RadioSelect(choices=PRIORITY_CHOICES)
	)

	priority_ocr = forms.IntegerField(
		required=True,
		initial=0,
		widget=forms.RadioSelect(choices=PRIORITY_OCR_CHOICES)
	)


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

	return render(request, 'files/files_form.html', 
			{'form': form,	} )
	

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

	return render(request, 'files/files_form.html', 
			{'form': form, 'file': file } )

#
# Delete entry
#

def delete(request, pk):

	file = Files.objects.get(pk=pk)
	
	file.delete()

	return redirect('files:index')


#
# Add website to queue
# So a worker will download/read the file and import/download all new articles
#

def crawl(request, pk):

	file = Files.objects.get(pk=pk)
	
	# add to queue
	last_imported = datetime.datetime.now()

	from opensemanticetl.tasks import index_filedirectory

	index_filedirectory.apply_async( kwargs={ 'filename': file.uri }, queue='open_semantic_etl_tasks', priority=5 )

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

		# If delta 0, no automatic import
		if not file.delta:
			add_to_queue = False

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

			from opensemanticetl.tasks import index_filedirectory

			index_filedirectory.apply_async( kwargs={ 'filename': file.uri }, queue='open_semantic_etl_tasks', priority=5 )


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


def prioritize(request):

	setup = Setup.objects.get(pk=1)

	if request.method == 'POST': # If the form has been submitted...
		form = PrioritizeForm(request.POST) # A form bound to the POST data
		if form.is_valid():

			filename = form.cleaned_data['filename']
			priority = form.cleaned_data['priority']

			priority_ocr = form.cleaned_data['priority_ocr']

			if priority_ocr == 0:
				priority_ocr = PRIORITY_TO_OCR_PRIORITY[priority]

			from opensemanticetl.enhance_mapping_id import mapping_reverse
			from opensemanticetl.tasks import index_file

			# read config file to get path mappings
			config = {'plugins': [], 'regex_lists': []}
			exec(open('/etc/opensemanticsearch/etl').read(), locals())
			exec(open('/etc/opensemanticsearch/connector-files').read(), locals())
			exec(open('/etc/opensemanticsearch/etl-webadmin').read(), locals())

			filename = mapping_reverse(filename, config['mappings'])

			additional_plugins_later = []
			if 'additional_plugins_later' in config:
				additional_plugins_later = config['additional_plugins_later']

			additional_plugins_later_config = {}
			if 'additional_plugins_later_config' in config:
				additional_plugins_later_config = config['additional_plugins_later_config']

			task_id = index_file.apply_async( kwargs={ 'filename': filename }, queue='open_semantic_etl_tasks', priority=priority )

			task_ocr_id = None

			if len(additional_plugins_later) > 0 or len(additional_plugins_later_config) > 0:

	                        task_ocr_id = index_file.apply_async(kwargs={ 'filename': filename, 'additional_plugins': additional_plugins_later, 'config': additional_plugins_later_config}, queue='open_semantic_etl_tasks', priority=priority_ocr)

			return render(request, 'files/files_prioritize.html', 
				{	
					"form": form,
					'setup': setup,
					"task_id": task_id,
					"task_ocr_id": task_ocr_id,
				})

		else:
			return render(request, 'files/files_prioritize.html', {'form': form})

	else:
		filename = ''
		if 'url' in request.GET:
			filename = request.GET["url"]

		form = PrioritizeForm(initial={'filename': filename}) # An unbound form

		return render(request, 'files/files_prioritize.html', {'form': form})
