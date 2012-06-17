from django.conf.urls import patterns, url
from django.contrib.admin.views.decorators import staff_member_required
from .views import ApiView

urlpatterns = patterns('',
    url(r'^api/(?P<path>[a-z0-9][a-z0-9/]*)$', staff_member_required(ApiView.as_view()), name='api'),
)