from django.conf.urls import patterns, url

from files import views

urlpatterns = patterns('',
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
	url(r'^(?P<pk>\d+)/crawl$', 'files.views.crawl', name='crawl'),
	url(r'^recrawl$', 'files.views.recrawl', name='recrawl'),
	url(r'^create$', views.create_file, name='create'),
	url(r'^(?P<pk>\d+)/update$', views.update_file, name='update'),

)
