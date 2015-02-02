from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Capstone.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    (r'^polls/$', 'Sift.views.index'),
    (r'^polls/(?P<poll_id>\d+)/$', 'Sift.views.details'),
    (r'^polls/(?P<poll_id>\d+)/results/$', 'Sift.views.results'),
    (r'^polls/(?P<poll_id>\d+)/vote/$', 'Sift.views.vote'),
)
