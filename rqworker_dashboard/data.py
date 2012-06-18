from . import setup_rq_connection
from rq.connections import get_current_connection
from rq.job import Job
from rq.queue import Queue
from rq.worker import Worker
from .utils import serialize_queues, serialize_job

class Data(object):

    @classmethod
    def __connect(cls):
        setup_rq_connection()

    @classmethod
    def workers(cls):
        cls.__connect()
        return [{'name': w.name, 'key': w.key, 'pid': w.pid, 'state': w.state, 'stopped': w.stopped, 'queues': w.queue_names()} for w in Worker.all()]

    @classmethod
    def queues(cls):
        cls.__connect()
        return serialize_queues(sorted(Queue.all()))

    @classmethod
    def queue(cls, name):
        cls.__connect()
        q = Queue(name)
        return {'name': q.name, 'count': q.count, 'jobs': q.job_ids}

    @classmethod
    def jobs(cls, queuename=None):
        cls.__connect()
        if queuename:
            queue = Queue(queuename)
            jobs = [serialize_job(Job(id)) for id in queue.job_ids]
            return jobs
        else:
            return [cls.jobs(queue.get('name')) for queue in cls.queues()]


    @classmethod
    def all(cls):
        cls.__connect()

        data = {
            'workers': cls.workers(),
            'queues': cls.queues(),
            'jobs': cls.jobs(),
        }

        return data