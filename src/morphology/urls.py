from django.conf.urls import url

from morphology import views

urlpatterns = [
	url(r'^$', 'morphology.views.index', name='index'),
	url(r'^concept/(?P<pk>\d+)$', 'morphology.views.morph_concept', name='morph_concept'),
]
