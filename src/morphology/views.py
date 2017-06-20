from django.shortcuts import render


from django.http import HttpResponse 
from django.shortcuts import render


from django import forms

from thesaurus.models import Concept

#import pysolr
import urllib
import json
import os

#stemmers = ['_text_','stemmed', 'stemmed_hunspell_en']
#stemmers = ['_text_','stemmed', 'stemmed_hunspell_de']
stemmers = ['content','_text_','stemmed','synonyms']


class ListForm(forms.Form):
	list = forms.CharField(widget=forms.Textarea)
	
	filterquery = forms.CharField(widget=forms.TextInput, required=False)

	prefix = forms.BooleanField(required=False, initial=True)
	suffix = forms.BooleanField(required=False, initial=True)


# recommend morphology by an concept of the thesaurus
def morph_concept(request, pk):

	# read preflabel, alternate labels and hidden labels and generate AND search query

	verbose = False

	uri_search="/search/?q="

	concept = Concept.objects.get(pk=pk)

	list = []

	if concept.query:
		list.append(concept.query)

	if concept.prefLabel:
		list.append(concept.prefLabel)
		list.append(concept.prefLabel + '*')
		list.append( '*' + concept.prefLabel)
		list.append( '*' + concept.prefLabel + '*')
		list.append(concept.prefLabel + '~')
	
	for alternate in concept.alternates():

		if alternate.query:
			list.append(alternate.query)

		list.append(alternate.altLabel)
		list.append(alternate.altLabel + '*')
		list.append( '*' + alternate.altLabel)
		list.append( '*' + alternate.altLabel + '*')
		list.append(alternate.altLabel + '~')

	for hidden in concept.hiddens():
		if hidden.query:
			list.append(hidden.query)

		list.append(hidden.hiddenLabel)
		list.append(hidden.hiddenLabel + '*')
		list.append( '*' + hidden.hiddenLabel)
		list.append( '*' + hidden.hiddenLabel + '*')
		list.append(hidden.hiddenLabel + '~')

	# do searches
	results, error_messages = search_list(list, verbose=verbose, filterquery=None, stemmers = stemmers)

	#todo: variable aggregated with words from all stemmers
	
	aggregation = []
	for line in list:
		for stemmer in stemmers:
			for result in results[line][stemmer]:
				if result not in aggregation:
					aggregation.append(result)
				
	# terms not yet in concepts thesaurus entry

	aggregation_new = []

	for term in aggregation:

		is_in_hidden = False
		
		for hidden in concept.hiddens():
			if hidden.hiddenLabel == term:
				is_in_hidden = True


		is_in_alternates = False
		
		for alternate in concept.alternates():
			if alternate.altLabel == term:
				is_in_alternates = True

		
		if not term == concept.prefLabel and not is_in_hidden and not is_in_alternates:
			aggregation_new.append(term)
				
	return render(request, 'morphology_concept.html', 
				{	
					"concept": concept,
					"aggregation": aggregation,
					"aggregation_new": aggregation_new,
					"uri_search": uri_search,
					"error_messages": error_messages,
					"stemmers": stemmers,

					"results": results,
				})


def index(request):

	verbose = False

	uri_search="/search/?q="


	if request.method == 'POST': # If the form has been submitted...
		form = ListForm(request.POST) # A form bound to the POST data
		if form.is_valid():

			list = form.cleaned_data['list']
			list = list.split("\n")

			filterquery = form.cleaned_data['filterquery']
			

			prefix = form.cleaned_data['prefix']
			suffix = form.cleaned_data['suffix']


			# do searches
			results, error_messages = search_list(list, verbose=verbose, filterquery=filterquery,	stemmers = stemmers)

			

			return render(request, 'morphology_index.html', 
				{	
					"form": form,
					"uri_search": uri_search,
					"error_messages": error_messages,
					"stemmers": stemmers,

					"results": results,
				})

		else:
			return render(request, 'morphology_index.html', {'form': form,})

	else:
		form = ListForm() # An unbound form

		return render(request, 'morphology_index.html', {'form': form,})


def search(query, filterquery=None, operator='AND', stemmers=[]):

	count = 0

# not yet with pysolr until it repairs encoding problem with unicode that cannot be encoded into utf-8
#	solr = pysolr.Solr(solr)
	
#	results = solr.search(query, **{
#		'fl': 'score',
#		'defType': 'edismax'
#	} )
	results = {}
	for stemmer in stemmers:
		results[stemmer] = []


	for stemmer in stemmers:
	
		# todo: read Solr URI from config
		uri = 'http://localhost:8983/solr/core1/select?df=' + stemmer +'&q.op=' + operator + '&wt=json&deftype=edismax&fl=id&limit=1000000&hl=true&hl.snippets=1000&hl.fragsize=1&hl.fl=' + stemmer
		uri += '&q=' + urllib.parse.quote( query )
	
		if filterquery:
			uri += '&fq=' + urllib.parse.quote( filterquery )
			
		request = urllib.request.urlopen( uri )
		encoding = request.info().get_content_charset('utf-8')
		data = request.read().decode(encoding)
		request.close()
	
		result = json.loads(data)
		
		count = result['response']['numFound']
			
		if count:
	
			for doc in result['response']['docs']:
				if 'highlighting' in result:
					if doc['id'] in result['highlighting']:
						if stemmer in result['highlighting'][doc['id']]:
							for value in result['highlighting'][doc['id']][stemmer]:
	
								# extract value from between <em></em>
								value = value[value.find('<em>')+4 : value.find('</em>')]
								if not value in results[stemmer]:
									results[stemmer].append(value)
	
	
	return results



def search_list(list, verbose=False, filterquery=None, stemmers=[] ):
	
	#todo queries_done als Sammlung zum ausschliessen mit for query_done in queries_done...
	
	error_messages=[]
	results = {}
	rowcount = 0

	for line in list:
		rowcount = rowcount + 1
		
		# strip emtpy
		line = line.strip()

		if not line=='':
			
#			try:
		
				
				results[line] = search(line, filterquery=filterquery, stemmers = stemmers )

		
#			except BaseException as e:
#				import sys

#				error_message = "Error: Exception while searching line {} ({}): {}".format(rowcount, line, e)
				
#				sys.stderr.write( error_message )
#				error_messages.append(error_message)

	return results, error_messages
