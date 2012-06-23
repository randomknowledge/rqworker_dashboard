import re
from django.http import HttpResponse
from django.views.generic.base import View, TemplateView
from .data import Data
from rq.job import requeue_job, cancel_job, Job
from . import RAISE_EXCEPTIONS
from . import enqueue, OPTIONS
from . import queueTestNormal, queueTestFail
from .utils.json import JSONSerializer
from .utils.log import logger


class ApiView(View):
    routes = [
        ['all'],
        ['workers'],
        ['queues'],
        ['test', 'add', re.compile(r'(normal|failing)')],
        ['queue', re.compile(r'([a-z0-9]{1,50})')],
        ['jobs', re.compile(r'([a-z0-9]{1,50})')],
        ['job', re.compile(r'([a-zA-Z0-9-]{1,50})'),
            re.compile(r'(requeue|delete)?')],
    ]

    def get(self, request, *args, **kwargs):
        path = re.sub(r'^/+', '', kwargs.get('path', ''))
        path = re.sub(r'/+$', '', path).split('/')

        funcandparms = self.get_function(path)
        try:
            handler = getattr(self, funcandparms.pop(0))
        except Exception, e:
            if RAISE_EXCEPTIONS:
                raise e
            else:
                logger.warning(e)
                return HttpResponse('Bad Request', status=400)

        try:
            context = handler(*funcandparms)
        except Exception, e:
            if RAISE_EXCEPTIONS:
                raise e
            else:
                logger.warning(e)
                return HttpResponse('Bad Request', status=400)

        """
        if handler == self.all:
            return HttpResponse(
                '{"workers": [{"name": "Zoidberg-Ubuntu.6662", "queues": ["default", "custom"], "pid": 6653, "state": "busy", "stopped": false, "key": "rq:worker:Zoidberg-Ubuntu.6662"}], "jobs": {"default": [{"origin": "default", "created_at": "2012-06-23 11:01:38+0200", "ended_at": null, "description": "rqworker_dashboard.queueTestNormal(\'normal test\')", "age": "0:00:37.116730", "enqueued_at": "2012-06-23 11:01:38+0200", "result": null, "exc_info": null, "id": "b6242363-8260-4b00-8f9d-9562eab0520a"}], "success": [{"origin": "default", "created_at": "2012-06-23 11:01:36+0200", "ended_at": null, "description": "rqworker_dashboard.queueTestNormal(\'normal test\')", "age": "0:00:39.117568", "enqueued_at": "2012-06-23 11:01:36+0200", "result": "S\'yay!\'\\np1\\n.", "exc_info": null, "id": "6dd6eaf3-8a02-44ea-be56-41c3b80183e4"}, {"origin": "default", "created_at": "2012-06-23 11:01:37+0200", "ended_at": null, "description": "rqworker_dashboard.queueTestNormal(\'normal test\')", "age": "0:00:38.118277", "enqueued_at": "2012-06-23 11:01:37+0200", "result": "S\'yay!\'\\np1\\n.", "exc_info": null, "id": "4aa82303-1c8d-4367-860d-7bae7eaa21e9"}, {"origin": "default", "created_at": "2012-06-23 11:01:35+0200", "ended_at": null, "description": "rqworker_dashboard.queueTestNormal(\'normal test\')", "age": "0:00:40.118938", "enqueued_at": "2012-06-23 11:01:35+0200", "result": "S\'yay!\'\\np1\\n.", "exc_info": null, "id": "6d6df238-e345-4522-a5a9-ddc2fc20edfb"}]}, "queues": [{"count": 1, "jobs": ["b6242363-8260-4b00-8f9d-9562eab0520a"], "name": "default"}, {"count": 3, "jobs": ["6dd6eaf3-8a02-44ea-be56-41c3b80183e4", "4aa82303-1c8d-4367-860d-7bae7eaa21e9", "6d6df238-e345-4522-a5a9-ddc2fc20edfb"], "name": "success"}, {"count": 0, "jobs": [], "name": "custom"}]}',
                mimetype='application/json'
            )
        """

        jsonSerializer = JSONSerializer()
        return HttpResponse(
                jsonSerializer.serialize(context, use_natural_keys=True),
                mimetype='application/json')

    def get_function(self, path):
        for route in self.routes:
            l = len(path)
            matches = []
            for i in range(l):
                try:
                    match = re.match(route[i], path[i])
                except Exception:
                    pass
                else:
                    if match:
                        matches.append(match)
            if len(matches) == l:
                return [match.group(0) for match in matches]

    def workers(self):
        return Data.workers()

    def queues(self):
        return Data.queues()

    def queue(self, name):
        return Data.queue(name)

    def jobs(self, queuename=None):
        return Data.jobs(queuename)

    def all(self):
        return Data.all()

    def job(self, *args):
        args = list(args)
        id = args.pop(0)

        Data.connect()

        if not args:
            return Data.job(id)
        else:
            action = args.pop(0)
        if action == 'requeue':
            requeue_job(id)
        elif action == 'delete':
            try:
                Job(id).refresh()
                cancel_job(id)
            except Exception, e:
                if RAISE_EXCEPTIONS:
                    raise e
                else:
                    logger.warn(e)
        return {'status': 'OK'}

    def test(self, add, *args):
        if not args:
            raise NotImplementedError

        if args[0] == "normal":
            enqueue(queueTestNormal, 'normal test')
        else:
            enqueue(queueTestFail, 'failing test')
        return {'status': 'OK'}


class DashboardView(TemplateView):
    template_name = 'rqworker_dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        return {'poll_interval': OPTIONS.get('poll_interval', 10)}
