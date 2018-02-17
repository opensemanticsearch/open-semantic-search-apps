from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template import RequestContext
from django.views import generic
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.contrib import messages

from ontologies.models import Ontologies

import thesaurus.views
from thesaurus.models import Facet
from thesaurus.models import Concept

from opensemanticetl.enhance_extract_text_tika_server import enhance_extract_text_tika_server
import opensemanticetl.export_solr

from solr_ontology_tagger import OntologyTagger

import os.path
import tempfile

from urllib.request import urlretrieve
from urllib.request import urlopen

import rdflib.util
from rdflib import Graph
from rdflib import RDFS


class OntologiesForm(ModelForm):

	class Meta:
		model = Ontologies
		fields = '__all__'

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

			write_named_entities_config(request=request)

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
			form.save()

			write_named_entities_config(request=request)

			return HttpResponseRedirect( reverse('ontologies:detail', args=[pk])) # Redirect after POST
		
			pass
	else:
		form = OntologiesForm(instance=ontology)

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
# Download graph from SPARQL endpoint
#

def download_rdf_from_sparql_endpoint(endpoint, query):

	from SPARQLWrapper import SPARQLWrapper, XML

	# read graph by construct query results from SPARQL endpoint
	sparql = SPARQLWrapper(endpoint)
	sparql.setQuery(query)
	sparql.setReturnFormat(XML)
	results = sparql.query().convert()

	# crate temporary filename
	file = tempfile.NamedTemporaryFile()
	filename = file.name
	file.close()

	# export graph to RDF file
	results.serialize(destination=filename, format="xml")


	return filename


#
# Get local file(name) of the ontology
#

# Therefore download to tempfile or reference to local file

def get_ontology_file(ontology):

	# if local file, file no temp file
	is_tempfile = False

	if os.path.isfile(ontology.file.path):

		filename = ontology.file.path

	elif ontology.sparql_endpoint:

		is_tempfile = True
		filename = download_rdf_from_sparql_endpoint(ontology.sparql_endpoint, ontology.sparql_query)

	elif ontology.uri.startswith('file://'):

		# filename is file URI without protocol prefix file://
		filename = ontology.uri[len('file://'):]

	else:
		# Download url to an tempfile
		is_tempfile = True
		filename, headers = urlretrieve(ontology.uri)

	return is_tempfile, filename


#
#  Tag indexed documents containing this entry or label(s) of every entry/entity in ontology or list
#

def tag_by_ontology(ontology):

	# get the ontology file
	is_tempfile, filename = get_ontology_file(ontology)
	
	facet =  get_facetname(ontology)

	contenttype, encoding = get_contenttype_and_encoding(filename)
	
	if contenttype == 'application/rdf+xml':

		ontology_tagger = OntologyTagger()

		#load graph from RDF file
		ontology_tagger.parse(filename)

		# tag the documents on Solr server with all matching entities of the ontology	
		ontology_tagger.apply(target_facet=facet)

	elif contenttype.startswith('text/plain'):
		tag_by_list(filename=filename, field=facet, encoding=encoding)
	
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

def tag_by_list(filename, field, encoding='utf-8'):

	# open and read plaintext file line for line

	file = open(filename, encoding=encoding)

	for line in file:
		
		value = line.strip()
	
		if value:

			# mask line/entry for search query			
			searchquery = "\"" + opensemanticetl.export_solr.solr_mask(value) + "\""
		
			solr = opensemanticetl.export_solr.export_solr()
			
			# tag the field/facet of all ducuments matching this query by value of entry
			count = solr.update_by_query( searchquery, field=field, value=value)

	file.close()


#
# Append entries/lines from an list/dictionary to another
#

def append_from_txtfile(sourcefilename, targetfilename, encoding='utf-8', wordlist_configfilename=None):
	
	appended_words = []

	source = open(sourcefilename, 'r', encoding=encoding)
	target = open(targetfilename, 'a', encoding="utf-8")


	if wordlist_configfilename:
		wordlist_file = open(wordlist_configfilename, 'a', encoding="UTF-8")

	for line in source:
		if line:
			target.write(line)

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
	target.close()

	if wordlist_configfilename:
		wordlist_file.close()


# An empty list file for a facet won't cause error opening/reading it, even if no entry exists
def if_not_exist_create_empty_list(targetfilename):

	target = open(targetfilename, 'a')
	target.close()


#
# Write Solr config to extract entries of generated lists/dictionaries to configured facets
#

def write_solr_schema_config(configfilename, facets):
	
	configfile = open(configfilename, 'w', encoding="utf-8")

	for facet in facets:

		configfile.write(	"""
<field name="{}" type="string" indexed="true" stored="true" multiValued="true"/>
<field name="{}_match" type="{}_match" indexed="true" stored="false" multiValued="true"/>
<copyField source="*" dest="{}_match"/>
<fieldType name="{}_match" class="solr.TextField" sortMissingLast="true" omitNorms="true">
<analyzer>
  <tokenizer class="solr.WhitespaceTokenizerFactory"/>
    <filter class="solr.ShingleFilterFactory"
            minShingleSize="2" maxShingleSize="5"
            outputUnigramsIfNoShingles="true"
    />
    <filter class="solr.KeepWordFilterFactory"
            words="named_entities/{}.txt" ignoreCase="true"/>
    <filter class="solr.LowerCaseFilterFactory"/>
  </analyzer>
</fieldType>
""".format(
					facet,
					facet,
					facet,
					facet,
					facet,
					facet
					)
	)
	
	configfile.close()


#
# Write facets config for search UI
#

# Collect all used facets so they can be displayed for search UI config

def write_facet_config(automatch_facets=[]):
	# Todo: maybe graph with labels or JSON instead of PHP config
	
	configfilename_php = '/etc/solr-php-ui/config.facets.php'
	configfilename_python = '/etc/opensemanticsearch/facets'
	
	configfile_php = open(configfilename_php, 'w', encoding="utf-8")
	configfile_python = open(configfilename_python, 'w', encoding="utf-8")

	configfile_php.write("<?php\n// do not config here, this config file will be overwritten by Thesaurus and Ontologies Manager\n")

	configfile_python.write("# do not config here, this config file will be overwritten by Thesaurus and Ontologies Manager\n")
	configfile_python.write("config['facets']={}\n")

	facets_done=[]

	# add facets of named entities
	for facet in Facet.objects.filter(enabled=True).order_by('facet_order'):
		facets_done.append(facet.facet)
		
		configfile_php.write("\n$cfg['facets']['{}'] = array ('label'=>'{}', 'facet_limit'=>'{}', 'snippets_limit'=>'{}'," . format( facet.facet, facet.label, facet.facet_limit, facet.snippets_limit))

		configfile_python.write( "config['facets']['{}'] = ". format(facet.facet) )
		configfile_python.write( "{" )
		configfile_python.write( "'label': '{}', 'uri': '{}', 'facet_limit': '{}', 'snippets_limit': '{}'," . format( facet.label, facet.uri, facet.facet_limit, facet.snippets_limit) )

		if facet.snippets_enabled:
			configfile_php.write("'snippets_enabled'=>true")
		else:
			configfile_php.write("'snippets_enabled'=>false")
		configfile_php.write(");\n")

		configfile_python.write("}\n")
		
		
		if facet.facet in automatch_facets:
			configfile_php.write("\n$cfg['facets']['{}_match'] = array ('label'=>'{} (automatic match)', 'facet_limit'=>'{}', 'snippets_limit'=>'{}',".format(	facet.facet, facet.label, facet.facet_limit, facet.snippets_limit))

			if facet.snippets_enabled:
				configfile_php.write("'snippets_enabled'=>true")
			else:
				configfile_php.write("'snippets_enabled'=>false")
			configfile_php.write(");\n")
	
	# add facets of ontolgoies
	for ontology in Ontologies.objects.all():

		facet = get_facetname(ontology)

		if facet not in facets_done:
		
			facets_done.append(facet)
			
			configfile_php.write("\n$cfg['facets']['{}'] = array ('label'=>'{}');\n".format(	facet, 	ontology	)	)
			if facet in automatch_facets:
				configfile_php.write("\n$cfg['facets']['{}_match'] = array ('label'=>'{} (automatic match)');\n".format(	facet, 	ontology	)	)

	configfile_php.write('?>')
	
	configfile_php.close()
	configfile_python.close()


#
# Clean facetname and listfilename
# so it can be used in XML configs within quotes
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
	elif ontology.title:
		facet = ontology.title
	elif ontology.file.name:
		# filename without path
		facet = os.path.basename(ontology.file.name)
	# not every uri can be used as filename, so dont use it, take better id
	#elif ontology.uri:
	#	facet = ontology.uri
	else:
		facet = "ontology_{}".format(ontology.id)

	facet = clean_facetname(facet)

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
		contenttype = data['content_type']

		# get charset if plain text file to extract with right charset
		if 'encoding_s' in data:
			encoding = data['encoding_s']
		else:
			encoding = 'utf-8'

		return contenttype, encoding


#
# Write entities to lists and add lists to Solr schema config
#

def	write_named_entities_config(request):

	solr_config_path = "/var/solr/data/core1/conf/named_entities"
	wordlist_configfilename = "/etc/opensemanticsearch/ocr/dictionary.txt"
	
	facets = []

	synonyms_configfilename = solr_config_path + os.path.sep + 'synonyms.txt'
	
	tmp_synonyms_configfilename = solr_config_path + os.path.sep + 'tmp_synonyms.txt'
	tmp_wordlist_configfilename = solr_config_path + os.path.sep + 'tmp_ocr_dictionary.txt'

	# create empty synonym config file for the case there are no synonyms in ontologies or thesaurus
	if_not_exist_create_empty_list(tmp_synonyms_configfilename)

	# create named entities configs for all ontologies
	for ontology in Ontologies.objects.all():
		
		try:
			print ("Importing Ontology or List {} (ID: {})".format( ontology, ontology.id ) )
		
			# Download, if URI
			is_tempfile, filename = get_ontology_file(ontology)
			
			facet = get_facetname(ontology)
		
			# analyse content type & encoding
			contenttype, encoding = get_contenttype_and_encoding(filename)
			print ( "Detected content type: {}".format(contenttype) )
			print ( "Detected encoding: {}".format(encoding) )


			# file to export all labels			
			tmplistfilename = solr_config_path + os.path.sep + 'tmp_' + facet + '.txt'
			
			#
			# export entries to listfiles
			#
						
			if contenttype=='application/rdf+xml':

				#
				# write labels, words and synonyms config files
				#

				ontology_tagger = OntologyTagger()

				# load graph from RDF file
				ontology_tagger.parse(filename)

				# don't tag documents in index, now we want only write the synonyms config
				ontology_tagger.solr = False
				
				# append synonyms to Solr config file
				ontology_tagger.synonyms_configfile = tmp_synonyms_configfilename

				# append single words of concept labels to wordlist for OCR word dictionary
				ontology_tagger.wordlist_configfile = tmp_wordlist_configfilename

				# append all labels to the facets labels list
				ontology_tagger.labels_configfile = tmplistfilename
				
				# write synonyms config file
				ontology_tagger.apply()

				
			elif contenttype.startswith('text/plain'):
				append_from_txtfile(sourcefilename=filename, targetfilename=tmplistfilename, encoding=encoding, wordlist_configfilename=tmp_wordlist_configfilename)
				
			else:
				# create empty list so configs of field in schema.xml pointing to this file or in facet config of UI will not break
				print ( "Unknown format {}".format(contenttype) )
				if_not_exist_create_empty_list(targetfilename=tmplistfilename)
	
			# remember each new facet for which there a list has been created so we can later write all this facets to schema.xml config part
			if not facet in facets:
				facets.append(facet)
			
			# Delete if downloaded ontology by URL to tempfile
			if is_tempfile:
				os.remove(filename)

		except BaseException as e:
			print ("Error: Exception while importing ontology {}: {}".format(ontology, e))
			messages.add_message( request, messages.ERROR, "Error: Exception while importing ontology {}: {}".format(ontology, e) )

	# Write thesaurus entries to facet entities list / dictionary
	thesaurus_facets = thesaurus.views.append_thesaurus_labels_to_dictionaries(synoynms_configfilename=tmp_synonyms_configfilename)

	# Append single words of concept labels to wordlist for OCR word dictionary
	thesaurus.views.append_concept_words_to_wordlist(wordlist_configfilename=tmp_wordlist_configfilename)

	# add facets used in thesaurus but not yet in an ontology to facet config
	for thesaurus_facet in thesaurus_facets:
		if not thesaurus_facet in facets:
			facets.append(thesaurus_facet)

	# Move new and complete facet file to destination
	for facet in facets:
		
		tmplistfilename = solr_config_path + os.path.sep + 'tmp_' + facet + '.txt'
		listfilename = solr_config_path + os.path.sep + facet + '.txt'
		os.rename(tmplistfilename, listfilename)

	# Move temp synonyms and OCR words config file to destination
	os.rename(tmp_synonyms_configfilename, synonyms_configfilename)
	os.rename(tmp_wordlist_configfilename, wordlist_configfilename)
	
	# Create config for schema.xml include for all facets
	configfilename = solr_config_path + os.path.sep + 'schema_named_entities.xml'
	write_solr_schema_config(configfilename, facets)
	
	# Create config for UI
	write_facet_config(automatch_facets=facets)
	
	# Reload/restart Solr core / schema / config to apply changed configs
	# so added config files / ontolgies / facets / new dictionary entries will be considered by analyzing/indexing new documents
	# Todo: Use the Solr URI from config
	urlopen('http://localhost:8983/solr/admin/cores?action=RELOAD&core=core1')

