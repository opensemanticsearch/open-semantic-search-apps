from django.conf.urls import patterns, url

urlpatterns = patterns('',
	url(r'^import$', 'rss_manager.views.import_feeds'),
)
