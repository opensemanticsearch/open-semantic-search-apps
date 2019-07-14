from django.http import HttpResponse 
from django.shortcuts import render

from opensemanticetl.etl_web import Connector_Web

from django import forms

from setup.models import Setup


class ListForm(forms.Form):
	list = forms.CharField(widget=forms.Textarea)
	

def index(request):

	verbose = False
	
	setup = Setup.objects.get(pk=1)


	if request.method == 'POST': # If the form has been submitted...
		form = ListForm(request.POST) # A form bound to the POST data
		if form.is_valid():

			list = form.cleaned_data['list']
			list = list.split()

			count = 0
			error_messages = []

			# exclude this urls
			exclude = ['rect']

			connector = Connector_Web(verbose=verbose)

			# search all the lines
			for uri in list:

				uri=uri.strip()

				if uri and not uri in exclude:
					try:
						connector.index(uri)
						count = count + 1
					except BaseException as e:
						error_messages.append("Exception while ETL process of {} : {}".format( uri, str(e) ) )
				

			return render(request, 'datasources.html', 
				{	
					"form": form,
					"count": count,
					"error_messages": error_messages,
				})

		else:
			return render(request, 'datasources.html', {'form': form, 'setup': setup})

	else:
		form = ListForm() # An unbound form

		return render(request, 'datasources.html', {'form': form, 'setup': setup })
