from django.conf.urls import url

from api import views

urlpatterns = [
	url(r'^delete', 'api.views.queue_delete', name='queue_delete'),
	url(r'^enrich', 'api.views.queue_enrich', name='queue_enrich'),
	url(r'^index-web', 'api.views.queue_index_web', name='queue_index_web'),
	url(r'^index-rss', 'api.views.queue_index_rss', name='queue_index_rss'),
	url(r'^index-file', 'api.views.queue_index_file', name='queue_index_file'),
	url(r'^index-dir', 'api.views.queue_index_file', name='queue_index_dir'),
]
