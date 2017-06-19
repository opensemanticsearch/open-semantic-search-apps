from django.conf.urls import patterns, url

from querytagger import views

urlpatterns = patterns('',
	url(r'^$', 'querytagger.views.index', name='index'),
)
