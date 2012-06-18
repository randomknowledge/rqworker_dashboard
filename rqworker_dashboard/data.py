from . import setup_rq_connection
from rq.job import Job
from rq.queue import Queue
from rq.worker import Worker
from .utils import serialize_queues, serialize_job

class Data(object):

    @classmethod
    def connect(cls):
        setup_rq_connection()

    @classmethod
    def workers(cls):
        cls.connect()
        return [{'name': w.name, 'key': w.key, 'pid': w.pid, 'state': w.state, 'stopped': w.stopped, 'queues': w.queue_names()} for w in Worker.all()]

    @classmethod
    def queues(cls):
        cls.connect()
        def compact_queue(q):
            q.compact()
            return q
        return serialize_queues(sorted(map(compact_queue, Queue.all())))

    @classmethod
    def queue(cls, name):
        cls.connect()
        q = Queue(name)
        q.compact()
        return {'name': q.name, 'count': q.count, 'jobs': q.job_ids}

    @classmethod
    def jobs(cls, queuename=None):
        cls.connect()
        if queuename:
            queue = Queue(queuename)
            queue.compact()
            jobs = [serialize_job(Job(id)) for id in queue.job_ids]
            return jobs
        else:
            return [cls.jobs(queue.get('name')) for queue in cls.queues()]

    @classmethod
    def job(cls, id):
        cls.connect()
        job = Job(id)
        try:
            job.refresh()
        except Exception, e:
            print e.message
            pass
        return serialize_job(job)



    @classmethod
    def all(cls):
        cls.connect()

        data = {
            'workers': cls.workers(),
            'queues': cls.queues(),
            'jobs': cls.jobs(),
        }

        return data