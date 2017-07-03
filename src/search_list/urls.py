from django.conf.urls import url

from search_list import views

urlpatterns = [
	url(r'^$', 'search_list.views.index', name='index'),
]
