from django.conf.urls import url

from morphology import views

urlpatterns = [
	url(r'^concept/(?P<pk>\d+)$', views.index, name="index"),
]
