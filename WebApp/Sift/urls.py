from django.conf.urls import patterns, url

from Sift import views

urlpatterns = patterns('',
                       # general analytics is the index
                       url(r'^$', views.general, name='general'),
                       # ex: topics/1
                       url(r'^topics/(?P<cluster_id>\d+)/$', views.details, name='details'),
                       # ex: /settings/
                       url(r'^settings/$', views.settings, name='settings'),

)