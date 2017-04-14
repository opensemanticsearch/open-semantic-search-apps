from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

	url(r'^admin/', include(admin.site.urls)),
	url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
	url(r'^api/', include('api.urls', namespace="api")),
	url(r'^crawler/', include('crawler.urls', namespace="crawler")),
	url(r'^files/', include('files.urls', namespace="files")),
	url(r'^datasources/', include('datasources.urls', namespace="datasources")),
	url(r'^annotate/', include('annotate.urls', namespace="annotate")),
	url(r'^thesaurus/', include('thesaurus.urls', namespace="thesaurus")),
	url(r'^rss_manager/', include('rss_manager.urls', namespace="rss_manager")),
	url(r'^querytagger/', include('querytagger.urls', namespace="querytagger")),
	url(r'^search-list/', include('search_list.urls', namespace="search_list")),
	url(r'^csv/', include('csv_manager.urls', namespace="csv_manager")),
	url(r'^ontologies/', include('ontologies.urls', namespace="ontologies")),
	url(r'^morphology/', include('morphology.urls', namespace="morphology")),
)
