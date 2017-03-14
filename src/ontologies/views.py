from django.shortcuts import render
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template import RequestContext
from django.views import generic
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.contrib import messages

from models import Ontologies

from thesaurus.models import Facet

from etl.enhance_extract_text_tika_server import enhance_extract_text_tika_server
import etl.export_solr

from solr_ontology_tagger import OntologyTagger

import os.path

import urllib

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

			write_named_entities_config()

			return HttpResponseRedirect( reverse('ontologies:detail', args=[ontology.pk]) ) # Redirect after POST

	else:
		form = OntologiesForm()

	return render_to_response('ontologies/ontologies_form.html', 
			{'form': form,	}, context_instance=RequestContext(request) )
	

#
# Updated an ontology, so rewrite/update named entity dictionaries and facet configs
#

def update_ontology(request, pk):

	ontology = Ontologies.objects.get(pk=pk)
	
	if request.POST:
		
		form = OntologiesForm(request.POST, request.FILES, instance=ontology)
		
		if form.is_valid():
			form.save()

			write_named_entities_config()

			return HttpResponseRedirect( reverse('ontologies:detail', args=[pk])) # Redirect after POST
		
			pass
	else:
		form = OntologiesForm(instance=ontology)

	return render_to_response('ontologies/ontologies_form.html', 
			{'form': form, 'ontology': ontology }, context_instance=RequestContext(request) )


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

	if os.path.isfile(ontology.file.name):
		filename = ontology.file.name
		
	elif ontology.uri.startswith('file://'):

		# filename is file URI without protocol prefix file://
		localfilename = ontology.uri[len('file://'):]

		if os.path.isfile(localfilename):
			filename = localfilename

	else:
		# Download url to an tempfile
		is_tempfile = True
		filename, headers = urllib.urlretrieve(ontology.uri)

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
		ontology_tagger.tag_documents(target_facet=facet)

	elif contenttype.startswith('text/plain'):
		tag_by_list(filename=filename, field=facet, encoding=encoding)
	
	else:
		# create empty list so configs of field in schema.xml pointing to this file or in facet config of UI will not break
		print "Unknown format {}".format(contenttype)
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

	file = open(filename)

	for line in file:
		line = line.decode(encoding)
		
		value = line.strip()
	
		if value:

			# mask line/entry for search query			
			searchquery = "\"" + etl.export_solr.solr_mask(value) + "\""
		
			solr = etl.export_solr.export_solr()
			
			# tag the field/facet of all ducuments matching this query by value of entry
			count = solr.update_by_query( searchquery, field=field, value=value)

	file.close()


#
# Append entries/lines from an list/dictionary to another
#

def append_from_txtfile(sourcefilename, targetfilename, encoding='UTF-8'):
	
	source = open(sourcefilename, 'r')
	target = open(targetfilename, 'a')

	for line in source:
		if line:
			target.write(line.decode(encoding).encode('UTF-8'))

	source.close()
	target.close()


#
# Read labels from RDF and append to list/dictionary to another
#

def append_from_rdffile(sourcefilename, targetfilename):

	target = open(targetfilename, 'a')

	g = Graph()
	
	#guess_format not in Ubuntus python_rdflib package yet
	#filetype = rdflib.util.guess_format(sourcefilename)

	#g.parse(sourcefilename, format = filetype)
	g.parse(sourcefilename)

	# get all RDFS labels
	for o in g.objects(None, RDFS.label):
		target.write(o.encode('UTF-8') + '\n')

	# SKOS labels
	skos = rdflib.Namespace('http://www.w3.org/2004/02/skos/core#')
		
	# append SKOS prefLabel
	for o in g.objects(None, skos['prefLabel']):
		target.write(o.encode('UTF-8') + '\n')

	# append SKOS altLabels
	for o in g.objects(None, skos['altLabel']):
		target.write(o.encode('UTF-8') + '\n')

	# append SKOS hiddenLabels
	for o in g.objects(None, skos['hiddenLabel']):
		target.write(o.encode('UTF-8') + '\n')

	target.close()


# An empty list file for a facet won't cause error opening/reading it, even if no entry exists
def if_not_exist_create_empty_list(targetfilename):

	target = open(targetfilename, 'a')
	target.close()


#
# Write Solr config to extract entries of generated lists/dictionaries to configured facets
#

def write_solr_config(configfilename, facets):
	
	configfile = open(configfilename, 'w')

	for facet in facets:

		configfile.write(	"""
<field name="{}" type="{}" indexed="true" stored="false" multiValued="true"/>
<copyField source="*" dest="{}"/>
<fieldType name="{}" class="solr.TextField" sortMissingLast="true" omitNorms="true">
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
</fieldType>""".format(
					facet.encode('utf-8'),
					facet.encode('utf-8'),
					facet.encode('utf-8'),
					facet.encode('utf-8'),
					facet.encode('utf-8')
					)
	)
	
	configfile.close()


#
# Write facets config for search UI
#

# Collect all used facets so they can be displayed for search UI config

def write_facet_config():
	# Todo: maybe graph with labels or JSON instead of PHP config
	
	configfilename = '/etc/solr-php-ui/config.facets.php'
	
	configfile = open(configfilename, 'w')
 	configfile.write("""<?php
// do not config here, this config file will be overwritten by Thesaurus and Ontologies Manager
""")

	facets_done=[]

	# add facets of named entities
	for facet in Facet.objects.all():
		facets_done.append(facet.facet)
		
		configfile.write(	"""
$cfg['facets']['{}'] = array ('label'=>'{}');
""".format(	facet.facet.encode('utf-8'), facet.label.encode('utf-8')	)	)

	# add facets of ontolgoies
	for ontology in Ontologies.objects.all():

		facet = get_facetname(ontology)

		if facet not in facets_done:
		
			facets_done.append(facet)
			
		 	configfile.write("""
$cfg['facets']['{}'] = array ('label'=>'{}');
""".format(	facet.encode('utf-8'), 	ontology.__unicode__().encode('utf-8')	)	)
	
	configfile.write('?>')
	
	configfile.close()


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
		parameters, data = tika.process(parameters=parameters)
		contenttype = data['content_type']

		# get charset if plain text file to extract with right charset
		if 'encoding_s' in data:
			encoding=data['encoding_s']
			print "Detected encoding: {}".format(encoding)
		else:
			encoding = 'UTF-8'

		return contenttype, encoding


#
# Write entities to lists and add lists to Solr schema config
#

# Todo: Do the same for thesaurus manager entries (better in its own module) via append and using this write named_entites config?

def	write_named_entities_config():

	solr_config_path = "/var/solr/data/core1/conf/named_entities"
	
	facets = []

	for ontology in Ontologies.objects.all():
		
		try:
			print "Importing Ontology or List {} (ID: {})".format( ontology, ontology.id )
		
			# Download, if URI
			is_tempfile, filename = get_ontology_file(ontology)
							
			facet = get_facetname(ontology)
		
			# analyse content type & encoding
			contenttype, encoding = get_contenttype_and_encoding(filename)
			
			# export entries to listfiles
			
			tmplistfilename = solr_config_path + os.path.sep + 'tmp_' + facet + '.txt'
			
			if contenttype=='application/rdf+xml':
				append_from_rdffile(sourcefilename=filename, targetfilename=tmplistfilename)
				
			elif contenttype.startswith('text/plain'):
	
				append_from_txtfile(sourcefilename=filename, targetfilename=tmplistfilename, encoding=encoding)
				
			else:
				# create empty list so configs of field in schema.xml pointing to this file or in facet config of UI will not break
				print "Unknown format {}".format(contenttype)
				if_not_exist_create_empty_list(targetfilename=tmplistfilename)
	
			# remember each new facet for which there a list has been created so we can later write all this facets to schema.xml config part
			if not facet in facets:
				facets.append(facet)
			
			# Delete if downloaded ontology by URL to tempfile
			if is_tempfile:
				os.remove(filename)

		except:
			print ("Error: Exception while importing ontology {}".format(ontology))
			messages.add_message( request, messages.ERROR, "Error: Exception while importing ontology {}".format(ontology) )

	# Move new and complete facet file to destination
	for facet in facets:
		
		tmplistfilename = solr_config_path + os.path.sep + 'tmp_' + facet + '.txt'
		listfilename = solr_config_path + os.path.sep + facet + '.txt'
		os.rename(tmplistfilename, listfilename)
		
	# Create config for schema.xml include for all facets
	configfilename = solr_config_path + os.path.sep + 'schema_named_entities.xml'
	write_solr_config(configfilename, facets)

	# Create config for UI
	write_facet_config()
	
	# Reload/restart Solr core / schema / config to apply changed configs
	# so added config files / ontolgies / facets / new dictionary entries will be considered by analyzing/indexing new documents
	# Todo: Use the Solr URI from config
	urllib.urlretrieve('http://localhost:8983/solr/admin/cores?action=RELOAD&core=core1')
	