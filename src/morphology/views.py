from django.shortcuts import render


from django.http import HttpResponse 
from django.shortcuts import render


from django import forms

from thesaurus.models import Concept
from setup.models import Setup

import urllib
import json
import os


class ListForm(forms.Form):
	list = forms.CharField(widget=forms.Textarea)
	
	filterquery = forms.CharField(widget=forms.TextInput, required=False)

	similar = forms.BooleanField(required=False, initial=True)

	prefix = forms.BooleanField(required=False, initial=True)
	suffix = forms.BooleanField(required=False, initial=True)
	
	limit = forms.IntegerField(required=False, initial=1000)


def index(request, pk):

	verbose = False

	uri_search = "/search/?q="

	stemmers = ['_text_']

	setup = Setup.objects.get(pk=1)

	if setup.languages:

		for language in setup.languages.split(','):
			stemmers.append('text_txt_' + language)

	if setup.languages_hunspell:
		for language in setup.languages_hunspell.split(','):
			languages.append('text_txt_hunspell_' + language)


	concept = Concept.objects.get(pk=pk)

	if request.method == 'POST': # If the form has been submitted...
		form = ListForm(request.POST) # A form bound to the POST data
		if form.is_valid():

			list = form.cleaned_data['list']
			list = list.replace("\r", "")
			list = list.split("\n")

			filterquery = form.cleaned_data['filterquery']
			
			prefix = form.cleaned_data['prefix']
			suffix = form.cleaned_data['suffix']

			similar = form.cleaned_data['similar']

			limit = form.cleaned_data['limit']

			variantlist = []
			
			for entry in list:

				terms = entry.split()

				if " " in entry:
					variantlist.append("\"" + entry + "\"")
				else:
					variantlist.append(entry)
				
				if prefix and suffix:
					terms_prefix_and_suffix = []
					for term in terms:
						terms_prefix_and_suffix.append( '*' + term + '*' )
					entry_prefix_and_suffix = " ".join(terms_prefix_and_suffix)
					if " " in entry_prefix_and_suffix:
						entry_prefix_and_suffix = "\"" + entry_prefix_and_suffix + "\""
					variantlist.append(entry_prefix_and_suffix)
					
				if prefix and not suffix:
					variantlist.append('*' + entry)
				
				if suffix and not prefix:
					variantlist.append(entry + '*')

				if similar:
					
					terms_similar = []
					for term in terms:
						terms_similar.append(term + "~")

					entry_similar = " ".join(terms_similar)
					if " " in entry_similar:
						entry_similar = "\"" + entry_similar + "\""
					
					variantlist.append(entry_similar)
		

			# do searches
			results, error_messages = search_list(variantlist, verbose=verbose, filterquery=filterquery, stemmers=stemmers, limit=limit)
		
			aggregation = []
			for line in variantlist:
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

			

			return render(request, 'morphology_index.html', 
				{	
					"is_result": True,
					"form": form,
					"concept": concept,
					"aggregation": aggregation,
					"aggregation_new": aggregation_new,
					"uri_search": uri_search,
					"error_messages": error_messages,
					"stemmers": stemmers,
					"results": results,
				})


		else:
			return render(request, 'morphology_index.html', {'is_result': False, 'form': form,})

	else:

		variantlist = []

		if concept.prefLabel:
			variantlist.append(concept.prefLabel)
	
		for alternate in concept.alternates():

			variantlist.append(alternate.altLabel)

		for hidden in concept.hiddens():

			variantlist.append(hidden.hiddenLabel)

				
		form = ListForm( initial = { 'list': "\n".join(variantlist) } ) # An unbound form

		return render(request, 'morphology_index.html', {'form': form,})


def search(query, filterquery=None, stemmers=[], limit=1000):

	count = 0

	results = {}

	for stemmer in stemmers:
		results[stemmer] = []


	for stemmer in stemmers:
	
		# todo: read Solr URI from config
		uri = 'http://localhost:8983/solr/opensemanticsearch/select?df=' + stemmer + '&wt=json&defType=complexphrase&fl=id&limit=' + str(limit) + '&hl=true&hl.snippets=1000&hl.fragsize=1&hl.fl=' + stemmer
		uri += '&q=' + urllib.parse.quote( query )

		print (uri)
	
		if filterquery:
			uri += '&fq=' + urllib.parse.quote( filterquery )
			
		request = urllib.request.urlopen( uri )
		encoding = request.info().get_content_charset('utf-8')
		data = request.read().decode(encoding)
		request.close()
	
		result = json.loads(data)
		
		count = result['response']['numFound']
			
		queryterms_count = len(query.split(" "))

		if count:
	
			for doc in result['response']['docs']:
				if 'highlighting' in result:
					if doc['id'] in result['highlighting']:
						if stemmer in result['highlighting'][doc['id']]:
							
							i = 0
							highlighted_terms = []
							
							for value in result['highlighting'][doc['id']][stemmer]:

								i += 1
	
								# extract value from between <em></em>
								term = value[value.find('<em>')+4 : value.find('</em>')]
	
								if i <= queryterms_count:
									highlighted_terms.append(term)
																		
								if i == queryterms_count:
									
									highlighted_phrase = " ".join(highlighted_terms)
									
									if not highlighted_phrase in results[stemmer]:
										results[stemmer].append(highlighted_phrase)

									i = 0
									highlighted_terms = []
	
	
	return results



def search_list(list, verbose=False, filterquery=None, stemmers=[], limit=1000 ):
	
	#todo queries_done als Sammlung zum ausschliessen mit for query_done in queries_done...
	
	error_messages=[]
	results = {}
	rowcount = 0

	for line in list:
		rowcount = rowcount + 1
		
		# strip emtpy
		line = line.strip()

		if not line=='':
			
			try:
		
				
				results[line] = search(line, filterquery=filterquery, stemmers = stemmers )

		
			except BaseException as e:
				import sys

				error_message = "Error: Exception while searching line {} ({}): {}".format(rowcount, line, e)
				
				sys.stderr.write( error_message )
				error_messages.append(error_message)

	return results, error_messages
