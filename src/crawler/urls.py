from django.conf.urls import patterns, url

from crawler import views

urlpatterns = patterns('',
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
	url(r'^(?P<pk>\d+)/crawl$', 'crawler.views.crawl', name='crawl'),
	url(r'^recrawl$', 'crawler.views.recrawl', name='recrawl'),
	url(r'^create$', views.create_crawler, name='create'),
	url(r'^(?P<pk>\d+)/update$', views.update_crawler, name='update'),

)
