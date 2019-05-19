from django.conf.urls import url

from api import views

urlpatterns = [
	url(r'^delete', views.queue_delete, name='queue_delete'),
	url(r'^enrich', views.queue_enrich, name='queue_enrich'),
	url(r'^index-web', views.queue_index_web, name='queue_index_web'),
	url(r'^index-rss', views.queue_index_rss, name='queue_index_rss'),
	url(r'^index-file', views.queue_index_file, name='queue_index_file'),
	url(r'^index-filedirectory', views.queue_index_file, name='queue_index_filedirectory'),
	url(r'^index-dir', views.queue_index_file, name='queue_index_dir'),
]
