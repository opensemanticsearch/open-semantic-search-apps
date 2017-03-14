from django.conf.urls import patterns, url

from annotate import views

urlpatterns = patterns('',
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^create$', 'annotate.views.create_annotation', name='create'),
	url(r'^edit$', 'annotate.views.edit_annotation', name='edit'),
	url(r'^rdf$', 'annotate.views.rdf', name='rdf'),
	url(r'^(?P<pk>\d+)/update$', 'annotate.views.update_annotation', name='update'),
	url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
)
