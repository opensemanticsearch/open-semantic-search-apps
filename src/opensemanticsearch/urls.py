from django.conf.urls import include, url

from django.contrib import admin

from django.contrib import auth


urlpatterns = [
	url(r'^admin/', include(admin.site.urls)),
	url(r'^api/', include('api.urls', namespace="api")),
	url(r'^entity_rest_api/', include('entity_rest_api.urls', namespace="entity_rest_api")),
	url(r'^setup/', include('setup.urls', namespace="setup")),
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
	url(r'^hypothesis/', include('hypothesis.urls', namespace="hypothesis")),
	url(r'^graph/', include('visual_graph_explorer.urls', namespace="graph")),
	url(r'^search_entity/', include('search_entity.urls', namespace="search_entity")),
	url(r'^morphology/', include('morphology.urls', namespace="morphology")),
	url(r'^twitter/', include('twitter.urls', namespace="twitter")),
]
