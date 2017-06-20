from django.shortcuts import render

from django.http import HttpResponse 
from django.shortcuts import render

from opensemanticetl.export_solr import export_solr

from django import forms

class ListForm(forms.Form):
	query = forms.CharField(widget=forms.Textarea)
	target_field = forms.CharField()
	target_value = forms.CharField()

def index(request):

	if request.method == 'POST': # If the form has been submitted...
		form = ListForm(request.POST) # A form bound to the POST data
		if form.is_valid():

			query = form.cleaned_data['query']
			target_field = form.cleaned_data['target_field']
			target_value = form.cleaned_data['target_value']

			connector = export_solr()
			results = connector.update_by_query(query=query, field=target_field, value=target_value)

			return render(request, 'querytagger/querytagger_index.html', 
				{	"form": form,
					"found": results,
					"query": query,
					"results": True,
				})
		else:
			return render(request, 'querytagger/querytagger_index.html', {'form': form,}) 
	else:
		form = ListForm(initial={'target_field': 'tag_ss',
								'target_value': 'myTag'}) # An unbound form
		
		
		return render(request, 'querytagger/querytagger_index.html', {'form': form,}) 