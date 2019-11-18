from django.conf.urls import url

from search_entity import views

urlpatterns = [
	url(r'^$', views.ambigous, name='ambigous'),
	url(r'^index$', views.index, name='index'),
]
