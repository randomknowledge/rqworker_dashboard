import re
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.views.generic.base import View, TemplateView
from . import enqueue, queueTestNormal, queueTestFail
from .data import Data
from .utils import JSONSerializer

class ApiView(View):
    routes = [
        ['all'],
        ['workers'],
        ['queues'],
        ['queue', re.compile(r'([a-z0-9]+)')],
        ['jobs', re.compile(r'([a-z0-9]+)')],
    ]

    def get(self, request, *args, **kwargs):
        path = re.sub( r'^/+', '', kwargs.get('path',''))
        path = re.sub( r'/+$', '', path).split('/')

        funcandparms = self.get_function( path )
        try:
            handler = getattr(self, funcandparms[0])
        except Exception:
            raise Http404()

        try:
            if len(funcandparms) == 1:
                context = handler(request)
            else:
                context = handler(request, funcandparms[1])
        except Exception, e:
            raise Http404()

        jsonSerializer = JSONSerializer()
        return HttpResponse(jsonSerializer.serialize(context, use_natural_keys=True), mimetype='application/json')

    def get_function(self, path):
        for route in self.routes:
            l = len(path)
            matches = []
            for i in range(l):
                try:
                    match = re.match(route[i],path[i])
                except Exception:
                    pass
                else:
                    if match:
                        matches.append(match)
            if len(matches) == l:
                return [match.group(0) for match in matches]

    def workers(self, request):
        return Data.workers()

    def queues(self, request):
        return Data.queues()

    def queue(self, request, name):
        return Data.queue(name)

    def jobs(self, request, queuename):
        return Data.jobs(queuename)

    def all(self, request):
        return Data.all()


class TestsView(TemplateView):
    template_name = 'rqworker_dashboard/tests.html'

    def get(self, request, *args, **kwargs):
        queue = kwargs.get('queue','default')
        test = kwargs.get('test','')
        if test:
            if test == 'normal':
                enqueue( queueTestNormal, 'normal test', queue=queue )
            else:
                enqueue( queueTestFail, 'failing test', queue=queue )
            request.session['rqworker_dashboard_test'] = test
            request.session['rqworker_dashboard_queue'] = queue
            return redirect('rqworker_dashboard_tests')

        context = {
            'test': request.session.get('rqworker_dashboard_test'),
            'queue': request.session.get('rqworker_dashboard_queue'),
        }

        request.session['rqworker_dashboard_test'] = ''
        request.session['rqworker_dashboard_queue'] = ''
        return self.render_to_response(context)


class DashboardView(TemplateView):
    template_name = 'rqworker_dashboard/dashboard.html'