from django.shortcuts import render
from django.http import HttpResponse
from django.core.urlresolvers import reverse 
from django.template import RequestContext
from django.views import generic
from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import redirect
import django.core.urlresolvers
import os.path
from urllib.request import urlopen
import solr_ontology_tagger

from thesaurus.models import Concept, Alternate, Hidden, Group, GroupTag, ConceptTag, Facet, Broader, Narrower, Related

from opensemanticetl.export_solr import export_solr
from entity_manager.manager import Entity_Manager

class ConceptForm(ModelForm):

	groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), widget=forms.CheckboxSelectMultiple(), required=False)

	class Meta:
		model = Concept
		fields = '__all__'

	def clean(self):
		cleaned_data = super(ConceptForm, self).clean()
		
		prefLabel = cleaned_data.get("prefLabel")
		query = cleaned_data.get("query")

		if not (prefLabel or query):
			raise forms.ValidationError("Missing name or query!")
		
		return cleaned_data


class IndexView(generic.ListView):
	model = Concept


class DetailView(generic.DetailView):
	model = Concept


class CreateView(generic.CreateView):
	model = Concept


class UpdateView(generic.UpdateView):
	model = Concept
	
	
def update_concept(request, pk):

	concept = Concept.objects.get(pk=pk)
	
	AlternatesFormSet = inlineformset_factory( Concept, Alternate, can_delete=True, exclude=() )
	MispellingsFormSet = inlineformset_factory( Concept, Hidden, can_delete=True, exclude=() )
	TagsFormSet = inlineformset_factory( Concept, ConceptTag, can_delete=True, exclude=() )
	BroaderFormSet = inlineformset_factory( Concept, Broader, fk_name='concept', can_delete=True, exclude=() )
	NarrowerFormSet = inlineformset_factory( Concept, Narrower, fk_name='concept', can_delete=True, exclude=() )
	RelatedFormSet = inlineformset_factory( Concept, Related, fk_name='concept', can_delete=True, exclude=() )
    
	if request.POST:
		
		concept_form = ConceptForm(request.POST, request.FILES, instance=concept, prefix="concept")
		
		alternates_formset = AlternatesFormSet(request.POST, request.FILES, instance=concept, prefix="alternates")
		misspellings_formset = MispellingsFormSet(request.POST, request.FILES, instance=concept, prefix="misspellings")
		tags_formset = TagsFormSet(request.POST, request.FILES, instance=concept, prefix="tags")

		broader_formset = BroaderFormSet(request.POST, request.FILES, instance=concept, prefix="broader")
		narrower_formset = NarrowerFormSet(request.POST, request.FILES, instance=concept, prefix="narrower")
		related_formset = RelatedFormSet(request.POST, request.FILES, instance=concept, prefix="related")


		if concept_form.is_valid() and alternates_formset.is_valid() and misspellings_formset.is_valid() and tags_formset.is_valid() and broader_formset.is_valid() and narrower_formset.is_valid() and related_formset.is_valid():
			concept_form.save()
			alternates_formset.save()
			misspellings_formset.save()
			tags_formset.save()
			broader_formset.save()
			narrower_formset.save()
			related_formset.save()

			messages.add_message( request, messages.INFO, "Saved concept \"{}\"".format(concept.prefLabel) )
			
			# export to Open Semantic Entity Search API config
			export_entity(concept=concept)
		
			# tag all docs containing concept or one of its aliases
			tag_concept_and_message_stats(request=request, concept=concept)

			return HttpResponseRedirect( reverse('thesaurus:detail', args=[pk])) # Redirect after POST
		
			pass
	else:
		concept_form = ConceptForm(instance=concept, prefix="concept")

		alternates_formset = AlternatesFormSet(instance=concept, prefix="alternates")
		misspellings_formset = MispellingsFormSet(instance=concept, prefix="misspellings")
		tags_formset = TagsFormSet(instance=concept, prefix="tags")

		broader_formset = BroaderFormSet(instance=concept, prefix="broader")
		narrower_formset = NarrowerFormSet(instance=concept, prefix="narrower")
		related_formset = RelatedFormSet(instance=concept, prefix="related")

	return render(request, 'thesaurus/concept_form.html',
			{'form': concept_form, 'concept': concept, 'alternates_formset':alternates_formset, 'misspellings_formset':misspellings_formset, 'tags_formset':tags_formset, 'broader_formset':broader_formset, 'narrower_formset':narrower_formset, 'related_formset':related_formset } )


def create_concept(request):

	if request.method == 'POST':
		form = ConceptForm(request.POST, request.FILES)
		if form.is_valid():
			concept = form.save()

			# export to Open Semantic Entity Search API config
			export_entity(concept=concept)

			# tag all docs containing concept or one of its aliases
			tag_concept_and_message_stats(request=request, concept=concept)

			return HttpResponseRedirect( reverse('thesaurus:detail', args=[concept.pk]) ) # Redirect after POST

	else:
		form = ConceptForm()

	return render(request, 'thesaurus/concept_form.html', 
			{'form': form,	} )


#
# API  to add new label with requested kind of relation
#
# Called by recommender

def api(request):

	concept_id = request.GET["id"]
	
	relation_name = request.GET["relation"]
	label = request.GET["label"]

	concept = Concept.objects.get(pk=concept_id)

	if relation_name == 'altLabel':
		   alternate = Alternate()
		   alternate.altLabel = label
		   alternate.concept = concept
		   alternate.save()
		
	if relation_name == 'hiddenLabel':
		   hidden = Hidden()
		   hidden.hiddenLabel = label
		   hidden.concept = concept
		   hidden.save()


	# todo:
	# find pk of concept else add concept if not yet there

	#if relation_name == 'broader':
	#if relation_name == 'narrower':
	#if relation_name == 'related':

	# export to Open Semantic Entity Search API config
	export_entity(concept=concept)
		
	# tag all docs containing concept or one of its aliases
	tag_concept_and_message_stats(request=request, concept=concept)


	return redirect(concept)


def tag_concept_and_message_stats(request, concept):
			count_queries, count_tagged, log = tag_concept(concept)
	
			if count_tagged:
				if count_queries > 1:
					messages.add_message(request, messages.INFO, "Tagged {} yet untagged documents matching the concept \"{}\" or one of its aliases while {} search queries".format(count_tagged, concept.prefLabel, count_queries) )
				else:
					messages.add_message(request, messages.INFO, "Tagged {} yet untagged documents matching the concept \"{}\"".format(count_tagged, concept.prefLabel) )
	
				messages.add_message(request, messages.INFO, "Log: " + ";\n".join(log))
			else:
				messages.add_message(request, messages.INFO, "No yet untagged documents matching the concept \"{}\" or one of its aliases (checked {} search queries)".format(concept.prefLabel, count_queries) )


# Add facets of groups and their parents to data
def get_grouptags(group, default_facet="tag_ss", data=None):

	if not data:
		data = {}

	# if facet add title to facet
	if group.facet:
		data = add_value_to_facet(facet=group.facet.facet, value=group.prefLabel, data=data)

	# add all tags to data
	for grouptag in GroupTag.objects.filter(group = group.id):
		
		if grouptag.facet.facet:
			facet = grouptag.facet.facet
		else:
			facet = default_facet

		data = add_value_to_facet(facet=facet, value=grouptag.prefLabel, data=data)

	# if parent, recursive call to add all tags of all parents
	if group.parent:
		data = get_grouptags(group.parent, default_facet=default_facet, data=data)

	return data


# Build a Solr searchquery
def build_searchquery(label, query, querytype=None):
	
	if not query:
		query = label
		
	if not querytype:
		querytype = "PHRASE"

	if querytype == 'PHRASE':
		maskphrase = True
		
		# if phrase yet enclosed with doublequotes by user, do not again
		if query.startswith('"') and query.endswith('"'):
			maskphrase = False

		# since deftype complexquery doesnt work with only one word in a phrase
		# and it is not a phrase because of missing space dont mask the phrase
		if not " " in query:
			maskphrase = False
		
		# more than one words should be a phrase, not a query which will found documents containing all words but in another context
		if maskphrase:
			query = '"' + query + '"'

	# if phrase and wildcards set parser to complexphrase so that we can use wildcards within phrases, too
	if "\"" in query and ( "*" in query or "?" in query ):
		queryparameters = { 'defType': 'complexphrase' }
	else:
	# else use edismax, since it allows to search for wildcard on beginning of term, too
		queryparameters = { 'defType': 'edismax' }
		
	if querytype == "OR":
		queryparameters['q.op'] = 'OR'
	else:
		# seems not to work if there are other AND / OR parameters in query
		queryparameters['q.op'] = 'AND'
		
	return query, queryparameters


def tag_concepts(request):
	
	sum_queries = 0
	sum_tagged = 0

	log_sum = []

	for concept in Concept.objects.all():
		
		# tag all docs containing concept or one of its aliases
		try:
			count_queries, count_tagged, log = tag_concept(concept)
	
			# sum stats
			sum_queries += count_queries
			sum_tagged += count_tagged
			log_sum.extend(log)

		except:
			message = "Error while searching or tagging the concept \"{}\"".format(concept.prefLabel)
			log_sum.append(message)
		
	# print stats
	stats = "Search queries: {}\n(checking if new documents with concept or alias but without tags of the concept or its groups)\n\n".format(sum_queries)
	stats += "Update queries (documents tagged): {}\n\n".format(sum_tagged)
	stats += "\n".join(log_sum)

	# return response
	status = HttpResponse(stats)
	status["Content-Type"] = "text/plain"
	
	return status


def add_value_to_facet(facet, value, data = None ):

	if not data:
		data = {}

	if facet in data:
		# if not list, convert to list
		if not isinstance(data[facet], list):
			data[facet] = [ data[facet] ]
		data[facet].append(value)
	else:
		data[facet] = value

	return data


def tag_concept(concept):

	# Todo: For more performance do only one query/search for all labels and aliases of the concept

	verbose = False

	default_facet = "tag_ss"

	count_queries = 0
	count_tagged = 0
	
	connector = export_solr( config = {'verbose': verbose} )
	
	log = []

	if verbose:
		log.append( "Checking concept: {}" . format(concept.prefLabel) )

	# if no entity facet use default facet
	if concept.facet:
		facet = concept.facet.facet
	else:
		facet = default_facet

	# add entity title to facet
	value = concept.prefLabel

	# if no prefLabel, use the query as value for tagging
	if not value:
		value = concept.query

	tagdata = add_value_to_facet(facet=facet, value=value)


	# Tag with all additional tags
	for concepttag in ConceptTag.objects.filter(concept = concept.id):

		# if no concepttag facet use default facet
		if concepttag.facet:
			facet = concepttag.facet.facet
		else:
			facet = default_facet

		# add concepttag title as values of this facet
		tagdata = add_value_to_facet(facet=facet, value=concepttag.label, data=tagdata)


	# Tag with all groups

	for group in concept.groups.all():
		tagdata = get_grouptags(group, default_facet=default_facet, data=tagdata)


	# build query searching for concept but only if not tagged yet (concept prefLabel not in target facet)
	searchquery, searchqueryparameters = build_searchquery(label=concept.prefLabel, query=concept.query, querytype=concept.query_type)

	if verbose:
		print ("Search query:")
		print (searchquery)
		print ("Search query parameters:")
		print (searchqueryparameters)

	count_queries += 1

	count = connector.update_by_query(query=searchquery, queryparameters=searchqueryparameters, data=tagdata)

	if count:
		count_tagged += count
		log.append ("Tagged {} yet untagged entries with tags of the concept \"{}\"".format(count, concept.prefLabel) )


	# Search aliases and tag them, too
	for alternate in Alternate.objects.filter(concept = concept.id):

		if verbose:
			log.append( "Checking alias: {}".format(alternate.altLabel) )
	
		searchquery, searchquery_parameters = build_searchquery(label=alternate.altLabel, query=alternate.query, querytype=alternate.query_type)

		count_queries += 1
		count = connector.update_by_query(query=searchquery, queryparameters=searchquery_parameters, data=tagdata)

		if count:
			count_tagged += count
			
			log.append ("Tagged {} yet untagged entries containing alias \"{}\" with tags of the concept \"{}\"".format( count, alternate.altLabel, concept.prefLabel ) )


	# Search aliases and tag them, too
	for hidden in Hidden.objects.filter(concept = concept.id):

		if verbose:
			log.append( "Checking hidden label: {}".format(hidden.hiddenLabel) )
	
		searchquery, searchquery_parameters = build_searchquery(label=hidden.hiddenLabel, query=hidden.query, querytype=hidden.query_type)

		count_queries += 1
		count = connector.update_by_query(query=searchquery, queryparameters=searchquery_parameters, data=tagdata)

		if count:
			count_tagged += count
			
			log.append ("Tagged {} yet untagged entries containing hidden label \"{}\" with tags of the concept \"{}\"".format( count, hidden.hiddenLabel, concept.prefLabel ) )

	return count_queries, count_tagged, log


#
# Write thesaurus entries to facet entities list / dictionary and to synonym config
#

def export_entities(wordlist_configfilename=None):

	facets = []
	appended_words=[]

	for concept in Concept.objects.all():
		
		appended_words = export_entity(concept=concept, wordlist_configfilename=wordlist_configfilename, appended_words = appended_words)

		if concept.facet:
			facet = concept.facet.facet
		else:
			facet = "tag_ss"
	
		if not facet in facets:
			facets.append(facet)
	
	return facets


#
# get full taxonomy with all broader concepts
#

def get_taxonomy(concept, path_ids=None, path_labels=None, results=[]):

	if not path_labels:
		path_labels = [ str(concept) ]

	if not path_ids:
		path_ids = []


	pks_broader = []

	# get ids/primary keys of broader concept(s)
	for relation in Broader.objects.filter(concept=concept):
		pks_broader.append(relation.broader.id)

	# same, if concept is narrower in other concept(s)
	for relation in Narrower.objects.filter(narrower=concept):
		pks_broader.append(relation.concept.id)

	# add id to yet or now traversed ids stack
	extended_path_ids = path_ids.copy()
	extended_path_ids.append(concept.id)

	traversal_done = True
	
	# recursion, if broader concepts
	for pk in pks_broader:

		# pk not in yet traversed path_ids (stack for loop detection stoping traversal, if a broader concept has a relation of type broader to one of its narrower yet traversed children)
		if not pk in extended_path_ids:
			
			traversal_done = False
			broader_concept = Concept.objects.get(pk=pk)
					
			extended_path_labels=path_labels.copy()
			extended_path_labels.append(str(broader_concept))
			results = get_taxonomy(concept=broader_concept, path_ids=extended_path_ids, path_labels=extended_path_labels, results=results)

	if traversal_done:
		# reverse the traversal path to start with broadest, not outgoing concept
		path_labels.reverse()
		results.append("\t".join(path_labels))
				
	return results



#
# Append concept labels and aliases to facet dictionary and write aliases to synonyms config file
#

def export_entity(concept, wordlist_configfilename = "/etc/opensemanticsearch/ocr/dictionary.txt", appended_words = []):
	
	facet = "tag_ss"
	if concept.facet:
		facet = concept.facet.facet

	altLabels = []
	for alternate in Alternate.objects.filter(concept = concept.id):
		altLabels.append(alternate.altLabel)
	for hidden in Hidden.objects.filter(concept = concept.id):
		altLabels.append(hidden.hiddenLabel)
			
	entity_manager = Entity_Manager()
	
	fields = {}

	# taxonomy
	taxonomy = get_taxonomy(concept)
	
	if taxonomy:
		fields['skos_broader_taxonomy_prefLabel_ss'] = taxonomy

	
	entity_manager.add(id=concept.pk, types=[facet], preferred_label=concept.prefLabel, prefLabels=[concept.prefLabel], labels=altLabels, fields=fields)


	# Append single words of concept labels to wordlist of OCR word dictionary
	labels = [concept.prefLabel]
	labels.extend(altLabels)

	if wordlist_configfilename:
		wordlist_file = open(wordlist_configfilename, 'a', encoding="UTF-8")
		for label in labels:
			words = label.split()
			for word in words:
				word = word.strip("(),")
				if word:
					if word not in appended_words:
						appended_words.append(word)
						appended_words.append(word.upper())
						wordlist_file.write(word + "\n")
						wordlist_file.write(word.upper() + "\n")
		wordlist_file.close()
	
	return appended_words