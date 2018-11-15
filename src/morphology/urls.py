from django.conf.urls import url

from morphology import views

urlpatterns = [
	url(r'^$', views.index, name="index"),
]
