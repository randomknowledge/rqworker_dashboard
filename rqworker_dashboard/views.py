import re
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.views.generic.base import View, TemplateView
from . import setup_rq_connection
from rq.job import Job
from rq.worker import Worker, Queue
from . import enqueue, queueTestNormal, queueTestFail
from .utils import serialize_queues
from .utils import serialize_job
from .utils import JSONSerializer

class ApiView(View):
    routes = [
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

        setup_rq_connection()

        try:
            if len(funcandparms) == 1:
                context = handler(request)
            else:
                context = handler(request, funcandparms[1])
        except Exception, e:
            raise e
            #raise Http404()

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
        return [{'name': w.name, 'key': w.key, 'pid': w.pid, 'state': w.state, 'stopped': w.stopped} for w in Worker.all()]

    def queues(self, request):
        queues = serialize_queues(sorted(Queue.all()))
        return dict(queues=queues)

    def queue(self, request, name):
        q = Queue(name)
        return {'name': q.name, 'count': q.count, 'jobs': q.job_ids}

    def jobs(self, request, queuename):
        queue = Queue(queuename)
        jobs = [serialize_job(Job(id)) for id in queue.job_ids]
        return dict(name=queue.name, jobs=jobs)

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