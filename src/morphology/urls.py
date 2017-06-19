from django.conf.urls import patterns, url

from morphology import views

urlpatterns = patterns('',
	url(r'^$', 'morphology.views.index', name='index'),
	url(r'^concept/(?P<pk>\d+)$', 'morphology.views.morph_concept', name='morph_concept'),

)
