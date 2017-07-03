from django.conf.urls import url

from csv_manager import views

urlpatterns = [
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^create$', views.CreateView.as_view(), name='create'),
	url(r'^(?P<pk>\d+)/update$', views.UpdateView.as_view(), name='update'),
	url(r'^(?P<pk>\d+)/index_csv$', views.index_csv, name='index_csv'),
	url(r'^(?P<pk>\d+)/preview$', views.preview_csv, name='preview_csv'),
	url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
]
