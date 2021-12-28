from django.conf.urls import url

from annotate import views

urlpatterns = [
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^create$', views.create_annotation, name='create'),
	url(r'^edit$', views.edit_annotation, name='edit'),
	url(r'^json$', views.export_json, name='export_json'),
	url(r'^rdf$', views.export_rdf, name='export_rdf'),
	url(r'^(?P<pk>\d+)/update$', views.update_annotation, name='update'),
	url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
]
