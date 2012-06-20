from . import setup_rq_connection
from rq.job import Job
from rq.queue import Queue
from rq.worker import Worker
from .utils import serialize_queues, serialize_job, remove_ghost_workers


class Data(object):

    @classmethod
    def connect(cls):
        setup_rq_connection()

    @classmethod
    def workers(cls):
        cls.connect()
        remove_ghost_workers()
        return [{'name': w.name, 'key': w.key,
            'pid': w.pid, 'state': w.state, 'stopped': w.stopped,
            'queues': w.queue_names()} for w in Worker.all()]

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
            j = {}
            for queue in cls.queues():
                n = queue.get('name')
                j[n] = cls.jobs(n)
            return j

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

        workers = cls.workers()
        queues = cls.queues()

        def make_queue_dict(q):
            return dict(name=q, count=0, jobs=[])

        def has_queue(queues, name):
            for q in queues:
                if q.get('name') == name:
                    return True
            return False

        if workers:
            for w in workers:
                wqueues = map(make_queue_dict, w.get('queues', []))
                for wqueue in wqueues:
                    if not has_queue(queues,wqueue.get('name')):
                        queues.append(wqueue)

        data = {
            'workers': workers,
            'queues': queues,
            'jobs': cls.jobs(),
        }

        return data
