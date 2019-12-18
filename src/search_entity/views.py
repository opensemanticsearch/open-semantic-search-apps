from django.shortcuts import render

from django.http import HttpResponse 
from django.shortcuts import render

import json
import os
import requests

from collections import Counter


solr = "http://localhost:8983/solr/"
if os.getenv('OPEN_SEMANTIC_ETL_SOLR'):
	solr = os.getenv('OPEN_SEMANTIC_ETL_SOLR')

solr_core = "opensemanticsearch-entities"



def solr_mask(string_to_mask, solr_specialchars = '\+-&|!(){}[]^"~*?:/'):
	
		masked = string_to_mask
		# mask every special char with leading \
		for char in solr_specialchars:
			masked = masked.replace(char, "\\" + char)
			
		return masked


def solr_search(query=None, operator="PHRASE", limit=1000, fields=None, queryfields=None, filterquery=None, raw_params=None, solr_core = "opensemanticsearch-entities"):
		
	url = solr + solr_core + "/" + "select"

	params = {"wt": "json", "defType": "edismax", "sow":"false", "rows": limit}

	if fields:
		params["fl"] = fields


	if queryfields:
		params["qf"] = queryfields

	if filterquery:
		params["fq"] = filterquery

	if query:
		solr_query = solr_mask(query)
	else:
		solr_query = '*:*'

	if operator=="PHRASE":
		if not solr_query == '*:*':
			solr_query = "\"" + solr_query + "\""
	else:
		params["q.op"] = operator
	
	params["q"] = solr_query
	
	if raw_params:
		for key in raw_params:
			params[key] = raw_params[key]
		
	response = requests.get(url, params = params)

	response = response.json()
	
	return response



def ambigous(request):

	
			queryfields = [	'label_ss^2',
						'preferred_label_s^20',
						'skos_prefLabel_ss^10',
						'skos_altLabel_ss^5',
						'skos_hiddenLabel_ss^1',
						'all_labels_ss^1'
				]
			
			raw_params = {'facet': 'true', 'facet.field': 'all_labels_ss', 'facet.limit': 10000, 'facet.mincount': 2}
			searchresults = solr_search(limit=0, raw_params=raw_params)
			facetvalues = []
			for facet in searchresults['facet_counts']['facet_fields']:		
				
				is_value = True
				for value in searchresults['facet_counts']['facet_fields'][facet]:
					if is_value:
						facet_value = value
		
						# next list entry is count
						is_value=False
					else:
						facet_count = value

						facetvalues.append( {facet_value: facet_count} )
						
						# next list entry is a value
						is_value = True
		

			return render(request, 'search_entity/search_entity_list.html', 
				{
					
					"facetvalues": facetvalues,

				})


def index(request):

	fields = 'id,preferred_label_s,all_labels_ss'

	filterquery = None

	query = None
	
	entity_id = None
	
	doc_id = None
	matchtexts = []

	raw_params = {}

	if 'label' in request.GET:
		query = request.GET["label"]
		raw_params = { 'facet': 'true', 'facet.field': 'all_labels_ss' }
	else:
		entity_id = request.GET['id']
		filterquery = 'id:(' + solr_mask(entity_id)  + ')'
		
	if 'doc' in request.GET:
		doc_id = request.GET['doc']

	queryfields = [	'label_ss^2',
				'preferred_label_s^20',
				'skos_prefLabel_ss^10',
				'skos_altLabel_ss^5',
				'skos_hiddenLabel_ss^1',
				'all_labels_ss^1'
		]
	

	searchresults = solr_search(query, queryfields=queryfields, fields=fields, filterquery=filterquery, raw_params=raw_params)
	
	entities = []
	counts = {}
	
	for result in searchresults['response']['docs']:
		entity = { 'id': result['id'], 'preferred_label_s': result['preferred_label_s'] }
		labels = []
		done = []
	
		for label in result['all_labels_ss']:
	
			if not label in done:
				done.append(label)
				if label in counts:
					count = counts[label]
				else:
					count = count_documents(solr=solr, solr_core='opensemanticsearch', query=label, operator="PHRASE", fields='content_txt')
					counts[label] = count

				labels.append( {label: count} )

		
		entity['labels'] = labels

		entities.append(entity)
			
	# Sort counts to array in descending order
	counts = Counter(counts).most_common()

	# if parameter document id, read matches of thesaurus entry in document
	if doc_id:

		filterquery = 'id:("' + solr_mask(doc_id)  + '")'

		searchresults = solr_search(filterquery=filterquery, solr_core = "opensemanticsearch")
	
		for result in searchresults['response']['docs']:
			for field in result:
				if field.endswith('_matchtext_ss'):
					values = result[field]
					if not isinstance(values, list):
						values = [values]

					for value in values:
						if value.startswith(entity_id + "\t"):
							print (value)
							matchtext = value[len(entity_id)+1:]
							print (matchtext)
							matchtexts.append (matchtext)
	

	return render(request, 'search_entity/search_entity.html', 
		{
			"query": query,
			"entity_id": entity_id,
			"entities": entities,
			"counts": counts,
			"doc": doc_id,
			"matchtexts": matchtexts,
			
		})



#
# how many documents for query in index?
#
def count_documents(solr, solr_core, query, operator="PHRASE", fields=None, filterquery=None):

	url = solr + solr_core + "/" + "select"

	params = {"wt": "json", "defType": "edismax", "sow":"false", "rows": 0}

	if fields:
		params["qf"] = fields

	# do not search for segments of other documents like indexed single pages
	params["fq"] = ['-content_type_ss:"PDF page"']

	if filterquery:
		params["fq"].append(filterquery)

	solr_query = solr_mask(query)

	if operator=="PHRASE":
		solr_query = "\"" + solr_query + "\""
	else:
		params["q.op"] = operator
	
	params["q"] = solr_query
		
	response = requests.get(url, params = params)

	r = response.json()

	numFound = r['response']['numFound']
	
	return numFound
