from django.conf.urls import url

from thesaurus import views

urlpatterns = [
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^create$', views.create_concept, name='create'),
	url(r'^(?P<pk>\d+)/update$', views.update_concept, name='update'),
	url(r'^apply$', views.tag_concepts, name='apply'),
	url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
	url(r'^api', views.api, name='api'),
]
