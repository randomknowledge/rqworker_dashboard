from django.conf.urls import patterns, url
from django.contrib.admin.views.decorators import staff_member_required
from .views import ApiView, TestsView

urlpatterns = patterns('',
    url(r'^api/(?P<path>[a-z0-9][a-z0-9/]*)$', staff_member_required(ApiView.as_view()), name='rqworker_dashboard_api'),
    url(r'^$', staff_member_required(TestsView.as_view()), name='rqworker_dashboard_tests'),
    url(r'^addtest/(?P<queue>default|custom)/(?P<test>normal|fail)$', staff_member_required(TestsView.as_view()), name='rqworker_dashboard_tests_add'),
)