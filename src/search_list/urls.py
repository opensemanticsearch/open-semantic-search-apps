from django.conf.urls import patterns, url

from search_list import views

urlpatterns = patterns('',
	url(r'^$', 'search_list.views.index', name='index'),
)
