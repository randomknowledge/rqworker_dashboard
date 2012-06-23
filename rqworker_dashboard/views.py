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
