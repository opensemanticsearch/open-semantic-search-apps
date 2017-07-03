from django.conf.urls import url

from datasources import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
]