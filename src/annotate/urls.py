from django.conf.urls import url

from annotate import views

urlpatterns = [
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^create$', views.create_annotation, name='create'),
	url(r'^edit$', views.edit_annotation, name='edit'),
	url(r'^rdf$', views.rdf, name='rdf'),
	url(r'^(?P<pk>\d+)/update$', views.update_annotation, name='update'),
	url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
]
