from django.conf.urls import patterns, include, url
from django.contrib import admin



urlpatterns = patterns('',
                       url(r'^', include('Sift.urls', namespace="general")),
                       url(r'^admin/', include(admin.site.urls)),
)