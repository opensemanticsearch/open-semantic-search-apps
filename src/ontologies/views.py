from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template import RequestContext
from django.views import generic
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.contrib import messages
from django import forms

from setup.models import Setup

from ontologies.models import Ontologies

import thesaurus.views
import setup.views

from thesaurus.models import Facet
from thesaurus.models import Concept

from opensemanticetl.enhance_extract_text_tika_server import enhance_extract_text_tika_server
import opensemanticetl.etl_sparql
import opensemanticetl.export_solr

from solr_ontology_tagger import OntologyTagger
from entity_import.entity_import_list import Entity_Importer_List

import os.path
import os
import tempfile
import shutil

from urllib.request import urlretrieve
from urllib.request import urlopen

# Grammar / Stemming languages
LANGUAGES_CHOICES = (
	('en', 'English'),
	('de', 'Deutsch (German)'),
	('hu', 'Hungarian'),
	('ru', 'Russian'),
)

LANGUAGES_CHOICES_HUNSPELL = (
	('hu', 'Hungarian'),
)



class OntologiesForm(ModelForm):

	class Meta:
		model = Ontologies
		exclude = ['stemming', 'stemming_force', 'stemming_hunspell', 'stemming_force_hunspell']

	stemming = forms.MultipleChoiceField(
		required=False,
		widget=forms.CheckboxSelectMultiple,
		choices=LANGUAGES_CHOICES,
    )

	stemming_force = forms.MultipleChoiceField(
		required=False,
		widget=forms.CheckboxSelectMultiple,
		choices=LANGUAGES_CHOICES,
    )

	stemming_hunspell = forms.MultipleChoiceField(
		required=False,
		widget=forms.CheckboxSelectMultiple,
		choices=LANGUAGES_CHOICES_HUNSPELL,
    )

	stemming_force_hunspell = forms.MultipleChoiceField(
		required=False,
		widget=forms.CheckboxSelectMultiple,
		choices=LANGUAGES_CHOICES_HUNSPELL,
    )

class IndexView(generic.ListView):
	model = Ontologies

class DetailView(generic.DetailView):
	model = Ontologies

class CreateView(generic.CreateView):
	model = Ontologies

class UpdateView(generic.UpdateView):
	model = Ontologies


#
# New/additional ontology, so rewrite/update named entity dictionaries and facet configs
#

def create_ontology(request):

	if request.method == 'POST':

		form = OntologiesForm(request.POST, request.FILES)

		if form.is_valid():
			ontology = form.save()

			write_named_entities_config()

			return HttpResponseRedirect( reverse('ontologies:detail', args=[ontology.pk]) ) # Redirect after POST

	else:
		form = OntologiesForm()

	return render(request, 'ontologies/ontologies_form.html', 
			{'form': form,	} )
	

#
# Updated an ontology, so rewrite/update named entity dictionaries and facet configs
#

def update_ontology(request, pk):

	ontology = Ontologies.objects.get(pk=pk)
	
	if request.POST:
		
		form = OntologiesForm(request.POST, request.FILES, instance=ontology)
		
		if form.is_valid():

			# manual handled MultipleChoiceField is saved comma separeted in a single CharField
			ontology.stemming = (',').join( form.cleaned_data['stemming'] )
			ontology.stemming_force = (',').join( form.cleaned_data['stemming_force'] )
			ontology.stemming_hunspell = (',').join( form.cleaned_data['stemming_hunspell'] )
			ontology.stemming_force_hunspell = (',').join( form.cleaned_data['stemming_force_hunspell'] )

			form.save()

			write_named_entities_config()

			return HttpResponseRedirect( reverse('ontologies:detail', args=[pk])) # Redirect after POST
		
			pass
	else:
		# The forms MultipleChoiceField is saved comma separeted in singe CharField,
		# so manual handling and turn over by form parameter initial
		stemming = ontology.stemming.split(",")
		stemming_force = ontology.stemming_force.split(",")
		stemming_hunspell = ontology.stemming_hunspell.split(",")
		stemming_force_hunspell = ontology.stemming_force_hunspell.split(",")

		form = OntologiesForm(instance=ontology, initial={ 'stemming': stemming, 'stemming_force': stemming_force, 'stemming_hunspell': stemming_hunspell, 'stemming_force_hunspell': stemming_force_hunspell })

	return render(request, 'ontologies/ontologies_form.html', 
			{'form': form, 'ontology': ontology } )


#
# Request to start to tag all untagged documents, that were indexed before with entities / labels of all ontologies
#

def apply_ontologies(request):

	count = 0

	for ontology in Ontologies.objects.all():
		
		count += 1

		tag_by_ontology(ontology)

	return render(request, 'ontologies/ontologies_apply_ontologies.html', {'count': count,})


#
# Request to tag all untagged documents, that were indexed before with entities / labels of an ontology
#

def apply_ontology(request, pk):


	ontology = Ontologies.objects.get(pk=pk)
	
	count = tag_by_ontology(ontology)
	
	return render(request, 'ontologies/ontologies_apply_ontology.html', {'id': pk, 'count': count,})


#
# Get local file(name) of the ontology
#

# Therefore download to tempfile or reference to local file

def get_ontology_file(ontology):

	# if local file, file no temp file
	is_tempfile = False

	if ontology.file:

		filename = ontology.file.path

	elif ontology.sparql_endpoint:
		
		is_tempfile = True

		if ontology.sparql_query.startswith("SELECT "):
			filename = opensemanticetl.etl_sparql.sparql_select_to_list_file(ontology.sparql_endpoint, ontology.sparql_query)
		else:
			filename = opensemanticetl.etl_sparql.download_rdf_from_sparql_endpoint(ontology.sparql_endpoint, ontology.sparql_query)

	elif ontology.uri.startswith('file://'):

		# filename is file URI without protocol prefix file://
		filename = ontology.uri[len('file://'):]

	else:
		# Download url to an tempfile
		is_tempfile = True
		filename, headers = urlretrieve(ontology.uri)

	print (filename)

	return is_tempfile, filename


#
# get the search fields for all configured languages
#
def get_stemmed_fields():

	setup = Setup.objects.get(pk=1)

	# default field
	fields = ['_text_']

	# configured languages / stemmers
	languages = []

	if setup.languages:
		languages.extend(setup.languages.split(','))

	if setup.languages_force:
		languages.extend(setup.languages_force.split(','))

	for language in languages:
		fieldname = 'text_txt_' + language
		if not fieldname in fields:
			fields.append(fieldname)


	# configured languages / hunspell stemmers
	languages_hunspell = []

	if setup.languages_hunspell:
		languages_hunspell.extend(setup.languages_hunspell.split(','))

	if setup.languages_force_hunspell:
		languages_hunspell.extend(setup.languages_force_hunspell.split(','))

	for language in languages_hunspell:
		fieldname = 'text_txt_hunspell_' + language
		if not fieldname in fields:
			fields.append(fieldname)

		

	return fields


#
#  Tag indexed documents containing this entry or label(s) of every entry/entity in ontology or list
#

def tag_by_ontology(ontology):

	# get the ontology file
	is_tempfile, filename = get_ontology_file(ontology)
	
	facet =  get_facetname(ontology)

	contenttype, encoding = get_contenttype_and_encoding(filename)
	
	queryfields = " ".join(get_stemmed_fields())
	
	if contenttype == 'application/rdf+xml':

		ontology_tagger = OntologyTagger()

		#load graph from RDF file
		ontology_tagger.parse(filename)

		# tag the documents on Solr server with all matching entities of the ontology	
		ontology_tagger.tag = True
		ontology_tagger.apply(target_facet=facet, queryfields=queryfields)

	elif contenttype.startswith('text/plain'):
		tag_by_list(filename=filename, field=facet, encoding=encoding, queryfields=queryfields)
	
	else:
		# create empty list so configs of field in schema.xml pointing to this file or in facet config of UI will not break
		print ( "Unknown format {}".format(contenttype) )

	#
	# Delete if downloaded ontology by URL to tempfile
	#
	if is_tempfile:
		os.remove(filename)


#
# Tag documents by dictionary in plaintext format
#

# Therefore search for each line of plaintextfile and add/tag the entity/entry/line to the facet/field of all documents matching this entry

def tag_by_list(filename, field, encoding='utf-8', queryfields='_text_'):

	# open and read plaintext file line for line

	file = open(filename, encoding=encoding)

	for line in file:
		
		value = line.strip()
	
		if value:

			# mask line/entry for search query			
			searchquery = "\"" + opensemanticetl.export_solr.solr_mask(value) + "\""
		
			solr = opensemanticetl.export_solr.export_solr()
			
			# tag the field/facet of all ducuments matching this query by value of entry
			count = solr.update_by_query( searchquery, field=field, value=value, queryparameters={'qf': queryfields} )

	file.close()


#
# Append entries/lines from an list/dictionary to list of separated words
#

def dictionary2wordlist(sourcefilename, encoding='utf-8', wordlist_configfilename=None):
	
	appended_words = []

	source = open(sourcefilename, 'r', encoding=encoding)

	wordlist_file = open(wordlist_configfilename, 'a', encoding="UTF-8")

	for line in source:
		if line:

			if wordlist_configfilename:
				# Append single words of concept labels to wordlist for OCR word dictionary

				words = line.split()
				for word in words:
					word = word.strip("(),")
					if word:
						if word not in appended_words:
							appended_words.append(word)
							appended_words.append(word.upper())
							wordlist_file.write(word + "\n")
							wordlist_file.write(word.upper() + "\n")


	source.close()

	wordlist_file.close()


#
# Write facets config for search UI
#

# Collect all used facets so they can be displayed for search UI config

def write_facet_config():
	# Todo: graph with labels or JSON instead of PHP config
	
	configfilename_php = '/etc/solr-php-ui/config.facets.php'
	configfilename_python = '/etc/opensemanticsearch/facets'
	
	configfile_php = open(configfilename_php, 'w', encoding="utf-8")
	configfile_python = open(configfilename_python, 'w', encoding="utf-8")

	configfile_php.write("<?php\n// do not config here, this config file will be overwritten by Thesaurus and Ontologies Manager\n")

	configfile_python.write("# do not config here, this config file will be overwritten by Thesaurus and Ontologies Manager\n")
	configfile_python.write("config['facets']={}\n")

	facets_done=[]

	configfile_php.write("\n$cfg['facets']['path'] = array ('label'=>'Path(s)', 'facet_limit'=>10, 'snippets_limit'=>10, 'graph_limit'=>0, 'snippets_enabled'=>false, 'graph_enabled'=>false, 'tree'=>true, 'closed'=>false);\n")


	# add facets of named entities
	for facet in Facet.objects.all().order_by('facet_order'):
		facets_done.append(facet.facet)
		
		configfile_php.write("\n$cfg['facets']['{}'] = array ('label'=>'{}', 'facet_limit'=>'{}', 'snippets_limit'=>'{}', 'graph_limit'=>'{}', 'tree'=>false" . format( facet.facet, facet.label, facet.facet_limit, facet.snippets_limit, facet.graph_limit))

		if facet.enabled:
			configfile_php.write(", 'enabled'=>true")
		else:
			configfile_php.write(", 'enabled'=>false")

		if facet.closed:
			configfile_php.write(", 'closed'=>true")
		else:
			configfile_php.write(", 'closed'=>false")

		if facet.snippets_enabled:
			configfile_php.write(", 'snippets_enabled'=>true")
		else:
			configfile_php.write(", 'snippets_enabled'=>false")

		if facet.graph_enabled:
			configfile_php.write(", 'graph_enabled'=>true")
		else:
			configfile_php.write(", 'graph_enabled'=>false")

		configfile_php.write(");\n")

		configfile_python.write( "config['facets']['{}'] = ". format(facet.facet) )
		configfile_python.write( "{" )
		configfile_python.write( "'label': '{}', 'uri': '{}', 'facet_limit': '{}', 'snippets_limit': '{}'," . format( facet.label, facet.uri, facet.facet_limit, facet.snippets_limit) )

		configfile_python.write("}\n")
			
	# add facets of ontolgoies
	for ontology in Ontologies.objects.all():

		facet = get_facetname(ontology)

		if facet not in facets_done:
		
			facets_done.append(facet)
			
			configfile_php.write( "\n$cfg['facets']['{}'] = array ('label'=>'{}', 'snippets_enabled'=>true);\n".format( facet, str(ontology) + ' (Exact match|List)' ) )
			configfile_php.write( "\n$cfg['facets']['{}_taxonomy'] = array ('label'=>'{}', 'tree'=>true, 'snippets_enabled'=>false, 'graph_enabled'=>false);\n".format( facet, str(ontology) + ' (Exact match|Taxonomy)' ) )

			
			# additional all labels fields for language dependent / additional analyzers/stemmers
			if ontology.stemming:
				for stemmer in ontology.stemming.split(','):
					configfile_php.write( "\n$cfg['facets']['{}'] = array ('label'=>'{}');\n".format( facet + 'all_labels_stemming_' + stemmer + '_ss_tag_ss', str(ontology) + ' (Fuzzy match by Porter stemmer ' + stemmer + ')' ) )

			if ontology.stemming_hunspell:
				for stemmer in ontology.stemming_hunspell.split(','):
					configfile_php.write( "\n$cfg['facets']['{}'] = array ('label'=>'{}');\n".format( facet + 'all_labels_stemming_hunspell_' + stemmer + '_ss_tag_ss', str(ontology) + ' (Fuzzy match by Hunspell stemmer ' + stemmer + ')' ) )

			configfile_python.write( "config['facets']['{}'] = ". format(facet) )
			configfile_python.write( "{" )
			configfile_python.write( "'label': '{}', 'uri': '{}', 'facet_limit': '{}', 'snippets_limit': '{}'," . format( ontology.title, ontology.uri, 0, 0) )

			configfile_python.write("}\n")

	configfile_php.write('?>')
	
	configfile_php.close()
	configfile_python.close()


#
# Clean facetname
#

def clean_facetname(facet):
	
	facet = facet.replace("\"", "")
	facet = facet.replace("\'", "")
	facet = facet.replace("\\", "")
	facet = facet.replace("/", "")
	facet = facet.replace("?", "")
	facet = facet.replace("&", "_")
	facet = facet.replace("$", "")
	facet = facet.replace("<", "")
	facet = facet.replace(">", "")
	facet = facet.replace("|", "_")
	facet = facet.replace(":", "_")
	facet = facet.replace(".", "_")
	facet = facet.replace(",", "_")
	facet = facet.replace(" ", "_")

	facet=facet.strip()
	
	return facet


#
# Mask facet name of the ontology
#

def get_facetname(ontology):

	if ontology.facet:
		facet = ontology.facet.facet
	else:
		if ontology.title:
			facet = ontology.title
		elif ontology.file.name:
			# filename without path
			facet = os.path.basename(ontology.file.name)
		# not every uri can be used as filename, so don't use it, take better id
		#elif ontology.uri:
		#	facet = ontology.uri
		else:
			facet = "ontology_{}".format(ontology.id)

		# remove special chars and add type suffix
		facet = clean_facetname(facet)
		facet = facet+'_ss'

	return facet


#
# Analyze contenttype (plaintextlist or ontology?) and encoding
#

def get_contenttype_and_encoding(filename):

		# use Tika and data enrichment/data analysis functions from ETL
		tika = enhance_extract_text_tika_server()
		parameters = {}
		parameters['filename'] = filename
		parameters, data = tika.process(parameters=parameters, data = {})
		contenttype = data['content_type_ss']

		# get charset if plain text file to extract with right charset
		if 'encoding_s' in data:
			encoding = data['encoding_s']
		else:
			encoding = 'utf-8'

		return contenttype, encoding


#
# Write entities configs
#

def	write_named_entities_config():

	# Solr host
	solr_url = 'http://localhost:8983/solr/'
	if os.getenv('OPEN_SEMANTIC_ETL_SOLR'):
		solr_url = os.getenv('OPEN_SEMANTIC_ETL_SOLR')

	wordlist_configfilename = "/etc/opensemanticsearch/ocr/dictionary.txt"
	
	tmp_wordlist_configfilename = tempfile.gettempdir() + os.path.sep +  next(tempfile._get_candidate_names()) + '_ocr_dictionary.txt'

	facets = []

	# create named entities configs for all ontologies
	for ontology in Ontologies.objects.all():
		
		print ("Importing Ontology or List {} (ID: {})".format( ontology, ontology.id ) )
	
		# Download, if URI
		is_tempfile, filename = get_ontology_file(ontology)
		
		facet = get_facetname(ontology)
	
		# analyse content type & encoding
		contenttype, encoding = get_contenttype_and_encoding(filename)
		print ( "Detected content type: {}".format(contenttype) )
		print ( "Detected encoding: {}".format(encoding) )


		#
		# export entries to entities index
		#
		
		if contenttype=='application/rdf+xml':

			#
			# write labels, words and synonyms config files
			#

			ontology_tagger = OntologyTagger()

			# load graph from RDF file
			ontology_tagger.parse(filename)

			# add the labels to entities index for normalization and entity linking
			ontology_tagger.solr_entities = solr_url
			ontology_tagger.solr_core_entities = 'opensemanticsearch-entities'
			
			# append synonyms to Solr managed synonyms resource "skos"
			ontology_tagger.solr = solr_url
			ontology_tagger.solr_core = 'opensemanticsearch'
			ontology_tagger.synonyms_resourceid = 'skos'

			# append single words of concept labels to wordlist for OCR word dictionary
			ontology_tagger.wordlist_configfile = tmp_wordlist_configfilename
			
			# additional all labels fields for language dependent / additional analyzers/stemmers
			if ontology.stemming:
				for stemmer in ontology.stemming.split(','):
					ontology_tagger.additional_all_labels_fields.append('all_labels_stemming_' + stemmer + '_ss')

			if ontology.stemming_force:
				for stemmer in ontology.stemming_force.split(','):
					ontology_tagger.additional_all_labels_fields.append('all_labels_stemming_force_' + stemmer + '_ss')

			if ontology.stemming_hunspell:
				for stemmer in ontology.stemming_hunspell.split(','):
					ontology_tagger.additional_all_labels_fields.append('all_labels_stemming_hunspell_' + stemmer + '_ss')

			if ontology.stemming_force_hunspell:
				for stemmer in ontology.stemming_force_hunspell.split(','):
					ontology_tagger.additional_all_labels_fields.append('all_labels_stemming_force_hunspell_' + stemmer + '_ss')

			# setup synonyms config and entities index
			ontology_tagger.apply(target_facet=facet)

		elif contenttype.startswith('text/plain'):
			dictionary2wordlist(sourcefilename=filename, encoding=encoding, wordlist_configfilename=tmp_wordlist_configfilename)
			importer = Entity_Importer_List()
			importer.import_entities(filename=filename, types=[facet], encoding=encoding)

		else:
			print ( "Unknown format {}".format(contenttype) )
		
		# remember each new facet for which there a list has been created so we can later write all this facets to schema.xml config part
		if not facet in facets:
			facets.append(facet)
		
		# Delete if downloaded ontology by URL to tempfile
		if is_tempfile:
			os.remove(filename)

	# Write thesaurus entries to facet entities list(s) / dictionaries, entities index and synonyms
	thesaurus_facets = thesaurus.views.export_entities(wordlist_configfilename=tmp_wordlist_configfilename)

	# add facets used in thesaurus but not yet in an ontology to facet config
	for thesaurus_facet in thesaurus_facets:
		if not thesaurus_facet in facets:
			facets.append(thesaurus_facet)

	# Move temp OCR words config file to destination
	if os.path.isfile(tmp_wordlist_configfilename):
		shutil.move(tmp_wordlist_configfilename, wordlist_configfilename)
	
	# Create config for UI
	write_facet_config()
	
	# Create config for ETL / entity extraction
	setup.views.generate_etl_configfile()
	
	# Reload/restart Solr core with new synonyms config
	# Todo: Use the Solr URI from config
	urlopen(solr_url + 'admin/cores?action=RELOAD&core=opensemanticsearch')

	# Commit and optimize entities index
	urlopen(solr_url + 'opensemanticsearch-entities/update?commit=true&optimize=true')

