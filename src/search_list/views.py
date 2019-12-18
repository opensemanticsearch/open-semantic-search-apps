from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from django.http import HttpResponse 
from django.shortcuts import render

from django import forms

import urllib
import json
import os

import opensemanticetl.export_solr
from opensemanticetl.export_solr import export_solr

class ListForm(forms.Form):
	list = forms.CharField(widget=forms.Textarea)
	
	filterquery = forms.CharField(widget=forms.TextInput, required=False)

	stopwords = forms.CharField(widget=forms.Textarea, required=False)
	
	raw = forms.BooleanField(required=False, initial=False)
	
	do_find_phrase = forms.BooleanField(required=False, initial=True)
	do_find_near = forms.BooleanField(required=False, initial=True)
	do_find_and = forms.BooleanField(required=False, initial=True)
	do_find_or = forms.BooleanField(required=False, initial=True)
	do_find_similar_and = forms.BooleanField(required=False, initial=True)
	do_find_similar_or = forms.BooleanField(required=False, initial=True)


def index(request):

	verbose = False

	uri_search="/search/?q="


	if request.method == 'POST': # If the form has been submitted...
		form = ListForm(request.POST) # A form bound to the POST data
		if form.is_valid():

			list = form.cleaned_data['list']
			list = list.split("\n")

			stopwords = form.cleaned_data['stopwords']
			filterquery = form.cleaned_data['filterquery']
			stopwords = stopwords.split("\n")
			

			do_find_phrase = form.cleaned_data['do_find_phrase']
			do_find_near = form.cleaned_data['do_find_near']
			do_find_and = form.cleaned_data['do_find_and']
			do_find_or = form.cleaned_data['do_find_or']
			do_find_similar_and = form.cleaned_data['do_find_similar_and']
			do_find_similar_or = form.cleaned_data['do_find_similar_or']

	
			
			# search all the lines
			(found, found_near, found_and, found_or, found_similar_and, found_similar_or, rowcount, error_messages) = search_list(list, verbose=verbose, filterquery=filterquery, stopwords=stopwords, do_find_phrase=do_find_phrase, do_find_near=do_find_near,do_find_and=do_find_and,do_find_or=do_find_or,do_find_similar_and=do_find_similar_and, do_find_similar_or=do_find_similar_or)

			return render(request, 'index.html', 
				{	
					"form": form,
					"uri_search": uri_search,
					"error_messages": error_messages,

					"results": found,
					"found": len(found),

					"results_near": found_near,
					"found_near": len(found_near),

					"results_and": found_and,
					"found_and": len(found_and),
					
					"results_similar_and": found_similar_and,
					"found_similar_and": len(found_similar_and),

					"results_or": found_or,
					"found_or": len(found_or),
					
					"results_similar_or": found_similar_or,
					"found_similar_or": len(found_similar_or),

					"rowcount": rowcount
				})

		else:
			return render(request, 'index.html', {'form': form,})

	else:
		form = ListForm() # An unbound form

		return render(request, 'index.html', {'form': form,}) #!/usr/bin/python


def clean_and_mask(query, operator = None, similar=False, stopwords=None):

	#todo: change NOT to not because if in name it should not be interpreted as search operator


	# clean and lowercase stopwords
	if stopwords:
		cleanedstopwords=[]
		for stopword in stopwords:
			
			stopword = stopword.strip()
			
			stopword = stopword.strip("\"")
			
			stopword = stopword.lower()
			
			cleanedstopwords.append(stopword)

		stopwords = cleanedstopwords

	else:
		stopwords = []
				

	query = query.strip()
	query = query.strip("\"")

	# strip beginning "-" (which sometimes is in names but would be interpreted as search operator that docs with this word would be excluded
	words = query.split()
	query = []
	for word in words:
		while word.startswith('-'):
			word = word.replace("-", '', 1)

		if not word.lower() in stopwords:

			word = opensemanticetl.export_solr.solr_mask(word)

			if similar:
				word = word + '~'

			query.append(word)
	
	if operator:
		delimiter = ' ' + operator + ' '
		query = delimiter.join(query)
	else:
		query = ' '.join(query)


	return query



def search(query, filterquery=None, operator='AND'):

	count = 0

	solr_host = 'http://localhost:8983/solr/'
	if os.getenv('OPEN_SEMANTIC_ETL_SOLR'):
		solr_host = os.getenv('OPEN_SEMANTIC_ETL_SOLR')

	uri = solr_host + 'opensemanticsearch/select?q.op=' + operator + '&wt=json&deftype=edismax&fl=id,score&hl=true&hl.fl=*'
	uri += '&q=' + urllib.parse.quote( query )

	if filterquery:
		uri += '&fq=' + urllib.parse.quote( filterquery )
		
	link = query
	
	request = urllib.request.urlopen( uri )
	encoding = request.info().get_content_charset('utf-8')
	data = request.read().decode(encoding)
	request.close()
	
	result = json.loads(data)

	count = result['response']['numFound']
	
	# preview data
	previews = None
	maxscore = 0
	if count:

		maxscore = str(result['response']['maxScore'])
	
		previews = []
		for doc in result['response']['docs']:
			score = doc['score']
			previews.append( {score:score} )
	
	return link, count, maxscore, previews



def search_list(list, verbose=False, filterquery=None, stopwords=None, do_find_phrase=True, do_find_near=True, do_find_and=True, do_find_or=True, do_find_similar_and=True, do_find_similar_or=True ):
	
	#todo queries_done als sammlung zum ausschliessen mit for query_done in queries_done...
	
	error_messages=[]
	rowcount = 0
	found = {}
	found_near = {}

	found_and = {}
	found_or = {}
	found_similar_and = {}
	found_similar_or = {}


	for line in list:
		
		# strip emtpy
		line = line.strip()

		if not line=='':
			
			rowcount = rowcount + 1

			try:
		
				#
				# exact matches with phrase search with "
				#
	
				query_phrase = "\"" + clean_and_mask(line) + "\""

				count = False
				if do_find_phrase:
					link, count, maxscore, previews = search(query_phrase, filterquery=filterquery)
	
				if count:
					found[line] = { 'count': count, 'link':link }
					if verbose:
						print ("Found " + str(count) +" for full phrase " + line)



				#
				# exact this words in this direction but allow words in between
				#
				max_words_between = 10
				query_near = "\"" + clean_and_mask(line, stopwords=stopwords) + "\"" + '~' + str(max_words_between)

				query = query_near
				
				# if yet searched, exclude former results
				if do_find_phrase:
					query = query + " AND NOT " + query_phrase

				count = False
				if do_find_near:
					link, count, maxscore, previews = search(query, filterquery=filterquery)
	
				if count:
					found_near[line] = { 'count': count, 'link':link, 'maxscore': maxscore, 'previews': previews }
					if verbose:
						print ("Found " + str(count) +" for full phrase with some words in between " + line)



				#
				# all words (and)
				#
				query_and = clean_and_mask(line, 'AND', stopwords=stopwords)
				
				query = query_and
				# if yet searched, exclude former results
				if do_find_phrase:
					query = query + " AND NOT " + query_phrase

				count = False
				if do_find_and:
					link, count, maxscore, previews = search(query, filterquery=filterquery)
	
				if count:
					found_and[line] = {'count': count, 'link':link, 'maxscore': maxscore, 'previews': previews }

					if verbose:
						print ("Maybe found (all words of phrase in document or row) " + str(count) + " for " + line)
		
		
		
				#
				# some words (or)
				#
				query_or = clean_and_mask(line, 'OR', stopwords=stopwords)

				query = "(" + query_or + ")"

				# if yet searched, exclude former results
				if do_find_and:
					query = query + " AND NOT (" + query_and + ")"

				if not do_find_and and do_find_phrase:
					query = query + " AND NOT (" + query_phrase + ")"
				
				count = False
				if do_find_or:

					link, count, maxscore, previews = search(query, filterquery=filterquery)
	
				if count:
					found_or[line] = {'count': count, 'link':link, 'maxscore': maxscore, 'previews': previews }
					if verbose:
						print ("Maybe found (some words of phrase in document or row) " + str(count) + " for " + line)
		

		
				#
				# similar words all (and)
				#
				query_similar_and = clean_and_mask(line, operator='AND', similar=True, stopwords=stopwords)

				query = "(" + query_similar_and + ")"

				# if yet searched, exclude former results
				if do_find_and:
					query = query + " AND NOT (" + query_and + ")"

				if not do_find_and and do_find_phrase:
					query = query + " AND NOT (" + query_phrase + ")"


				count = False
				if do_find_similar_and:
					link, count, maxscore, previews = search(query, filterquery=filterquery)
	
				if count:
					found_similar_and[line] = {'count': count, 'link':link, 'maxscore': maxscore, 'previews': previews }
					if verbose:
						print ("Maybe found (all words of phrase in document or row) " + str(count) + " for " + line)
		

		
				#
				# similar words some (or)
				#
				query_similar_or = clean_and_mask(line, operator='OR', similar=True, stopwords=stopwords)


				query = "(" + query_similar_or + ")"

				# if yet searched, exclude former results
				
				if do_find_and:
					query = query + " AND NOT (" + query_and + ")"
				if not do_find_and and do_find_phrase:
					query = query + " AND NOT (" + query_phrase + ")"
				
				if do_find_similar_and:
					query = query + " AND NOT (" + query_similar_and + ")"
	
				count = False
				if do_find_similar_or:
					link, count, maxscore, previews = search(query, filterquery=filterquery)

				if count:
					found_similar_or[line] = {'count': count, 'link':link, 'maxscore': maxscore, 'previews': previews }
					if verbose:
						print ("Maybe found (all words of phrase in document or row) " + str(count) + " for " + line)

		
			except BaseException as e:
				import sys

				error_message = "Error: Exception while searching line {}: {} - {}" .format(rowcount, line, e)
				
				sys.stderr.write( error_message )
				error_messages.append(error_message)


	return found, found_near, found_and, found_or, found_similar_and, found_similar_or, rowcount, error_messages
