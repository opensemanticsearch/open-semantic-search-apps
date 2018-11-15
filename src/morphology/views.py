from django.shortcuts import render
from django.http import HttpResponse 
from django.shortcuts import render
from django import forms

from thesaurus.models import Concept
from setup.models import Setup

import requests
import json
import os



solr_entities = "http://localhost:8983/solr/"
solr_core_entities = "opensemanticsearch-entities"



def solr_mask(string_to_mask, solr_specialchars = '\+-&|!(){}[]^"~*?:/'):
	
		masked = string_to_mask
		# mask every special char with leading \
		for char in solr_specialchars:
			masked = masked.replace(char, "\\" + char)
			
		return masked


def get_entity_labels(entity_id):

	labels = []	
	url = solr_entities + solr_core_entities + "/" + "select"

	params = {"wt": "json", "defType": "edismax", "qf": 'id', "fl": 'id,preferred_label_s,all_labels_ss' }

	solr_query = solr_mask(entity_id)

	params["q"] = solr_query
			
	r = requests.get(url, params = params)

	response = r.json()
	for label in response['response']['docs'][0]['all_labels_ss']:
		if not label in labels:
			labels.append(label)
			
	preferred_label = response['response']['docs'][0]['preferred_label_s']

	return preferred_label, labels


class ListForm(forms.Form):
	
	list = forms.CharField(widget=forms.Textarea)
	
	filterquery = forms.CharField(widget=forms.TextInput, required=False)

	similar = forms.BooleanField(required=False, initial=True)

	prefix = forms.BooleanField(required=False, initial=True)
	suffix = forms.BooleanField(required=False, initial=True)
	

def index(request):

	verbose = False

	uri_search = "/search/?q="

	exact_fields = ['_text_']

	stemmed_fields = []

	# todo: ignore false positives
	false_positives = []


	setup = Setup.objects.get(pk=1)

	if setup.languages:
		for language in setup.languages.split(','):
			stemmed_fields.append('text_txt_' + language)

	if setup.languages_hunspell:
		for language in setup.languages_hunspell.split(','):
			stemmed_fields.append('text_txt_hunspell_' + language)

	if request.method == 'POST': # If the form has been submitted...
		form = ListForm(request.POST) # A form bound to the POST data
		if form.is_valid():

			preferred_label = None
							
			entity_id = None
			if 'id' in request.GET:
				entity_id = request.GET['id']
	
			# read known labels from entity index
			if entity_id:
				preferred_label, labels = get_entity_labels(entity_id)
		
			list = form.cleaned_data['list']
			list = list.replace("\r", "")
			list = list.split("\n")

			filterquery = form.cleaned_data['filterquery']
			
			prefix = form.cleaned_data['prefix']
			suffix = form.cleaned_data['suffix']

			similar = form.cleaned_data['similar']

			querylist = []
			
			for entry in list:
		
				# if not empty line
				entry = entry.strip()
				if entry:
	
					terms = entry.split()
	
					if " " in entry:
						querylist.append("\"" + entry + "\"")
					else:
						querylist.append(entry)
					
					if prefix and suffix:
						terms_prefix_and_suffix = []
						for term in terms:
							terms_prefix_and_suffix.append( '*' + term + '*' )
						entry_prefix_and_suffix = " ".join(terms_prefix_and_suffix)
						if " " in entry_prefix_and_suffix:
							entry_prefix_and_suffix = "\"" + entry_prefix_and_suffix + "\""
						querylist.append(entry_prefix_and_suffix)
						
					if prefix and not suffix:
						querylist.append('*' + entry)
					
					if suffix and not prefix:
						querylist.append(entry + '*')
	
					if similar:
						
						terms_similar = []
						for term in terms:
							terms_similar.append(term + "~")
	
						entry_similar = " ".join(terms_similar)
						if " " in entry_similar:
							entry_similar = "\"" + entry_similar + "\""
						
						querylist.append(entry_similar)
		
			fields = exact_fields.copy()
			fields.extend(stemmed_fields)

			# do searches
			results, error_messages = search_list(querylist=querylist, verbose=verbose, filterquery=filterquery, fields=fields, known_variants=list.copy(), exact_fields=exact_fields)
				
			aggregation = []
			for line in querylist:
				for field in fields:
					for result in results[line][field]:
						if result not in aggregation:
							aggregation.append(result)
						
			# variant not yet in known variants
			aggregation_new = []
		
			for variant in aggregation:
				if not variant in list:
					aggregation_new.append(variant)
			

			return render(request, 'morphology_index.html', 
				{	
					"is_result": True,
					"preferred_label": preferred_label,
					"form": form,
					"entity_id": entity_id,
					"aggregation": aggregation,
					"aggregation_new": aggregation_new,
					"uri_search": uri_search,
					"error_messages": error_messages,
					"stemmers": fields,
					"results": results,
				})

		else:
			return render(request, 'morphology_index.html', {'is_result': False, 'form': form,})

	else:

		variantlist = ""
		preferred_label = None
		
		if 'list' in request.GET:
			variantlist = request.GET['list']
			
		entity_id = None
		if 'id' in request.GET:
			entity_id = request.GET['id']

		# read known labels from entity index
		if entity_id:
			preferred_label, labels = get_entity_labels(entity_id)
			variantlist += "\n".join(labels)

				
		form = ListForm( initial = { 'preferred_label': preferred_label, 'list': variantlist } ) # An unbound form

		return render(request, 'morphology_index.html', {'form': form,})


def get_matches(query, filterquery=None, fields=[], limit=50, known_variants=[], exact_fields=[]):

	count = 0
	
	max_iter = 50

	results = {}

	for field in fields:
		results[field] = []


	for field in fields:
		
		count_new_variants = 0

		for i in range(max_iter):
		
			# todo: read Solr URI from config
			uri = 'http://localhost:8983/solr/opensemanticsearch/select'
			
			params = {	'wt': 'json',
						'defType': 'complexphrase',
						'df': field,
						'fl': 'id',
						'limit': limit,
						'hl': 'true',
						'hl.snippets': 1000,
						'hl.fragsize': 1,
						'hl.fl': field,
						'q': query,
						}
				
		
			params['fq'] = []

			if filterquery:
				params['fq'].append(filterquery)
				

			for exact_field in exact_fields:
				for known_variant in known_variants:
					params['fq'].append( '-' + exact_field + ':(' + known_variant + ')' )
			
			r = requests.post(uri, data=params)

			result = json.loads(r.text)
			
			numFound = result['response']['numFound']
				
			if numFound:
				
				queryterms_count = len(query.split(" "))
		
				for doc in result['response']['docs']:
					if 'highlighting' in result:
						if doc['id'] in result['highlighting']:
							if field in result['highlighting'][doc['id']]:

								# todo: warn if count of highlitings in a doc on limit (parameter hl.snippets) and so matches maybe over limit
								i = 0
								highlighted_terms = []
								
								for value in result['highlighting'][doc['id']][field]:
	
									i += 1
		
									# extract value from between <em></em>
									term = value[value.find('<em>')+4 : value.find('</em>')]
		
									if i <= queryterms_count:
										highlighted_terms.append(term)
																			
									if i == queryterms_count:
										
										highlighted_phrase = " ".join(highlighted_terms)
										
										if not highlighted_phrase in results[field]:
											results[field].append(highlighted_phrase)
											known_variants.append(highlighted_phrase)
											
											# if many new variants, add additional max iterations
											if len(known_variants) * 2 > max_iter:
												max_iter = len(known_variants) * 2
	
										i = 0
										highlighted_terms = []

			# no further iteration/search for this field if no new/additional documents to last batch / (limited) samples
			if numFound < limit:
				break

	return results



def search_list(querylist, verbose=False, filterquery=None, fields=[], limit=50, known_variants=[], exact_fields=[] ):
		
	error_messages = []
	results = {}
	rowcount = 0

	for line in querylist:
		rowcount = rowcount + 1
		
		# strip emtpy
		line = line.strip()

		if not line=='':
			
			try:
				
				results[line] = get_matches(line, filterquery = filterquery, fields = fields, known_variants = known_variants, exact_fields=exact_fields)

			except BaseException as e:
				import sys

				error_message = "Error: Exception while searching line {} ({}): {}".format(rowcount, line, e)
				
				sys.stderr.write( error_message )
				error_messages.append(error_message)

	return results, error_messages
