from django.conf.urls import url

from setup import views

urlpatterns = [
	url(r'^$', views.update_setup, name='index'),
	url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
	url(r'^(?P<pk>\d+)/update$', views.update_setup, name='update'),
	url(r'^set_language$', views.setup_language, name='set_language'),
]