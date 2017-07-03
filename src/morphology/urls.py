from django.conf.urls import url

from morphology import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^concept/(?P<pk>\d+)$', views.morph_concept, name='morph_concept'),
]
