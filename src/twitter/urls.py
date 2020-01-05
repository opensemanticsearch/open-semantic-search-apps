from django.conf.urls import url

from twitter import views

urlpatterns = [
	url(r'^$', views.index, name="index"),
]
