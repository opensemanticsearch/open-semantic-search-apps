from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse 
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.forms import ModelForm
from django.views import generic
import django.forms as forms

from opensemanticetl.etl_enrich import ETL_Enrich

import urllib
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef

from annotate.models import Annotation
from thesaurus.models import Concept


# apply annotations to search index
def export_to_index(uri):

	etl = ETL_Enrich()
	etl.config['plugins'] = ['enhance_rdf_annotations_by_http_request']

	parameters = etl.config.copy()
	parameters['id'] = uri
	
	etl.process (parameters=parameters, data={})
	etl.commit()


class AnnotationForm(ModelForm):

	tags = forms.ModelMultipleChoiceField(queryset=Concept.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)

	class Meta:
		model = Annotation
		fields = '__all__'


class IndexView(generic.ListView):
	model = Annotation

class DetailView(generic.DetailView):
	model = Annotation

class UpdateView(generic.UpdateView):
	model = Annotation
	form_class = AnnotationForm
	
	
def update_annotation(request, id): 
    instance = MyModel.objects.get(id=id)
    form = MyForm(request.POST or None, instance=instance)
    if form.is_valid():
          form.save()
          return redirect('next_view')


def update_annotation(request, pk):

	annotation = Annotation.objects.get(pk=pk)

	if request.method == 'POST':
		form = AnnotationForm(request.POST, request.FILES, instance=annotation)
		if form.is_valid():
			annotation = form.save()
			
			# apply new data to search index
			export_to_index(annotation.uri)

			return HttpResponseRedirect( reverse('annotate:detail', args=[annotation.pk])) # Redirect after POST

	else:
			form = AnnotationForm(instance=annotation)
			

	return render(request, 'annotate/annotation_form.html', 
			{'form': form, } )



	
	

def create_annotation(request):

	if request.method == 'POST':
		form = AnnotationForm(request.POST, request.FILES)
		if form.is_valid():
			annotation = form.save()

			# apply new data to search index
			export_to_index(annotation.uri)

			return HttpResponseRedirect( reverse('annotate:detail', args=[annotation.pk])) # Redirect after POST

	else:

		if 'uri' in request.GET:
			initials = {
					"uri": request.GET['uri']
			}
			form = AnnotationForm(initial=initials)
		else:
			form = AnnotationForm()
			

	return render(request, 'annotate/annotation_form.html', 
			{'form': form, } )



def edit_annotation(request):

	uri = request.GET['uri']
	
	annotations = Annotation.objects.filter(uri=uri)

	if annotations:

		# get first primary key of annotation with given uri
		pk = annotations[0].pk
		annotation = Annotation.objects.get(pk=pk)
	
		#todo: warning message if more (if racing condition on creation)
	
		# redirect to edit this annotation
		return HttpResponseRedirect( reverse('annotate:update', args=[pk])) # Redirect after POST

	else:
		# no annotation for that uri, so redirect to create view
		return HttpResponseRedirect( "{}?uri={}".format( reverse('annotate:create'), urllib.parse.quote_plus( uri ) ) ) # Redirect after POST
		


# serialize tags for uri to RDF graph
def rdf(request):

	uri = request.GET['uri']
	
	g = Graph()
	
	annotations = Annotation.objects.filter(uri=uri)

	for annotation in annotations:

		if annotation.title:
			g.add( ( URIRef(annotation.uri), URIRef("http://localhost/metawiki/index.php/Special:URIResolver/Property-3ATitle"), Literal(annotation.title) ) )

		if annotation.notes:
			g.add( ( URIRef(annotation.uri), URIRef("http://localhost/metawiki/index.php/Special:URIResolver/Property-3ANotes"), Literal(annotation.notes) ) )

		for tag in annotation.tags.all():
			g.add( ( URIRef(annotation.uri), URIRef("http://localhost/metawiki/index.php/Special:URIResolver/Property-3ATag"), Literal(tag.prefLabel) ) )

	status = HttpResponse(g.serialize( format='xml' ) )
	status["Content-Type"] = "application/rdf+xml" 
	return status
	