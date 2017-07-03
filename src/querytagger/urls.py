from django.conf.urls import url

from querytagger import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
]
