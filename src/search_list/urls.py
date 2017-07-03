from django.conf.urls import url

from search_list import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
]
