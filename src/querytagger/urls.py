from django.conf.urls import url

from querytagger import views

urlpatterns = [
	url(r'^$', 'querytagger.views.index', name='index'),
]
