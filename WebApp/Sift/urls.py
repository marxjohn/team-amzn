from django.conf.urls import patterns, url

from Sift import views

urlpatterns = patterns('',
                       # general analytics is the index
                       url(r'^$', views.general, name='general'),
                       # ex: topics/1
                       url(r'^topics/(?P<cluster_id>\d+)/$',
                           views.details, name='details'),
                       # ex: /settings/
                       url(r'^settings/notifications/$', views.notifications,
                           name='notifications'),
                       # ex: /clustering/
                       url(r'^settings/clustering/$', views.clustering,
                           name='clustering'),
                       # ex: /clustering/
                       url(r'^clustering/$', views.clustering,
                           name='clustering'),
                       # ex: /cluster_running/
                       url(r'^settings/clusters/$', views.clusters,
                           name='clusters'),
                       # ex: /export_data/
                       url(r'^settings/exportdata/$', views.exportdata,
                           name='exportdata'),
                       url(r'^csv/$', views.exportdata)

                       )
