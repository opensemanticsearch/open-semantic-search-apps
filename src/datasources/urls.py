from django.conf.urls import url

urlpatterns = [
	url(r'^$', 'datasources.views.index', name='index'),
]