from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'RQWorkerDashboard.views.home', name='home'),
    # url(r'^RQWorkerDashboard/', include('RQWorkerDashboard.foo.urls')),

    url(r'^rq/', include('rqworker_dashboard.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
