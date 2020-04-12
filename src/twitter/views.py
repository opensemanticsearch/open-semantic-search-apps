from django.shortcuts import render
from django.http import HttpResponse 
from django.shortcuts import render
from django import forms

from setup.models import Setup

class ListForm(forms.Form):
		
	search = forms.CharField(widget=forms.TextInput, required=False)

	username = forms.CharField(widget=forms.TextInput, required=False)

	index_retweets = forms.BooleanField(required=False, initial=False)

	index_linked_webpages = forms.BooleanField(required=False, initial=False)

	limit = forms.IntegerField(required=False, initial=4000)


def index(request):

	setup = Setup.objects.get(pk=1)

	if request.method == 'POST': # If the form has been submitted...
		form = ListForm(request.POST) # A form bound to the POST data
		if form.is_valid():

			search = form.cleaned_data['search']
			username = form.cleaned_data['username']
			limit = form.cleaned_data['limit']

			index_retweets = form.cleaned_data['index_retweets']

			index_linked_webpages = form.cleaned_data['index_linked_webpages']

			from opensemanticetl.tasks import index_twitter_scraper

			task_id = index_twitter_scraper.apply_async( kwargs={ 'username': username, 'search': search, 'limit': limit, 'Profile_full': index_retweets, 'Index_Linked_Webpages': index_linked_webpages }, queue='open_semantic_etl_tasks', priority=6 )

			return render(request, 'twitter_index.html', 
				{	
					"form": form,
					'setup': setup,
					"task_id": task_id,
				})

		else:
			return render(request, 'twitter_index.html', {'form': form})

	else:
		form = ListForm() # An unbound form

		return render(request, 'twitter_index.html', {'form': form})
