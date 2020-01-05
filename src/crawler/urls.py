from django.conf.urls import url

from crawler import views

urlpatterns = [
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
	url(r'^(?P<pk>\d+)/crawl$', views.crawl, name='crawl'),
	url(r'^(?P<pk>\d+)/delete$', views.delete, name='delete'),
	url(r'^recrawl$', views.recrawl, name='recrawl'),
	url(r'^create$', views.create_crawler, name='create'),
	url(r'^(?P<pk>\d+)/update$', views.update_crawler, name='update'),
]
