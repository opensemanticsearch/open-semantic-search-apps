from django.conf.urls import url

from ontologies import views

urlpatterns = [
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
	url(r'^(?P<pk>\d+)/apply$', views.apply_ontology, name='apply_ontology'),
	url(r'^apply$', views.apply_ontologies, name='apply_ontologies'),
	url(r'^create$', views.create_ontology, name='create'),
	url(r'^(?P<pk>\d+)/update$', views.update_ontology, name='update'),
]
