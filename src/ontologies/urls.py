from django.conf.urls import patterns, url

from ontologies import views

	#url(r'^(?P<pk>\d+)/preview$', 'ontologies.views.preview_csv', name='preview_csv'),
#	url(r'^create$', views.CreateView.as_view(), name='create'),
#	url(r'^(?P<pk>\d+)/update$', views.UpdateView.as_view(), name='update'),

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
	url(r'^(?P<pk>\d+)/apply$', 'ontologies.views.apply_ontology', name='apply_ontology'),
	url(r'^apply$', 'ontologies.views.apply_ontologies', name='apply_ontologies'),
	url(r'^create$', views.create_ontology, name='create'),
	url(r'^(?P<pk>\d+)/update$', views.update_ontology, name='update'),

)
