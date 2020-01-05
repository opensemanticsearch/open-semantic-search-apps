from django.conf.urls import url

from rss_manager import views

urlpatterns = [
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
	url(r'^(?P<pk>\d+)/import$', views.import_feed, name='import_feed'),
	url(r'^(?P<pk>\d+)/delete$', views.delete, name='delete'),
	url(r'^import$', views.import_feeds, name='import_feeds'),
	url(r'^create$', views.create_feed, name='create'),
	url(r'^(?P<pk>\d+)/update$', views.update_feed, name='update'),
]
