from django.conf.urls import patterns, url
from django.contrib.admin.views.decorators import staff_member_required
from .views import ApiView, DashboardView

urlpatterns = patterns('',
    url(r'^api/(?P<path>[a-zA-Z0-9][a-zA-Z0-9/-]*)$', staff_member_required(ApiView.as_view()), name='rqworker_dashboard_api'),
    url(r'^$', staff_member_required(DashboardView.as_view()), name='rqworker_dashboard_index'),
)