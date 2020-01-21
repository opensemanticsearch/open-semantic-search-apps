from django.conf.urls import url

from files import views

urlpatterns = [
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
	url(r'^(?P<pk>\d+)/crawl$', views.crawl, name='crawl'),
	url(r'^(?P<pk>\d+)/delete$', views.delete, name='delete'),
	url(r'^recrawl$', views.recrawl, name='recrawl'),
	url(r'^create$', views.create_file, name='create'),
	url(r'^(?P<pk>\d+)/update$', views.update_file, name='update'),
	url(r'^prioritize$', views.prioritize, name='prioritize'),
]
