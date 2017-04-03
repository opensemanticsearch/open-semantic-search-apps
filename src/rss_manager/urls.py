from django.conf.urls import patterns, url

from rss_manager import views

urlpatterns = patterns('',
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
	url(r'^(?P<pk>\d+)/import$', 'rss_manager.views.import_feed', name='import_feed'),
	url(r'^import$', 'rss_manager.views.import_feeds', name='import_feeds'),
	url(r'^create$', views.create_feed, name='create'),
	url(r'^(?P<pk>\d+)/update$', views.update_feed, name='update'),

)
