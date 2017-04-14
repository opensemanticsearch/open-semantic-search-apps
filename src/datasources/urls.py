from django.conf.urls import patterns, url

urlpatterns = patterns('',
	url(r'^$', 'datasources.views.index', name='index'),
)
