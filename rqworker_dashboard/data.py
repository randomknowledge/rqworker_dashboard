from . import setup_rq_connection, get_current_connection
from rq.job import Job
from rq.queue import Queue
from rq.worker import Worker
from .utils.json import serialize_queues, serialize_job
from .utils.proc import remove_ghost_workers


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
        queues = serialize_queues(sorted(map(compact_queue, Queue.all())))
        queues.append(cls.queue('success'))
        return queues

    @classmethod
    def queue(cls, name):
        cls.connect()
        q = Queue(name)
        if name == 'success':
            jobs = cls.successful_jobs()
            return {'name': name, 'count': len(jobs), 'jobs': [j.get('id') for j in jobs]}
        else:
            q.compact()
        return {'name': q.name, 'count': q.count, 'jobs': q.job_ids}

    @classmethod
    def jobs(cls, queuename=None):
        cls.connect()
        if queuename:
            queue = Queue(queuename)
            if queuename != 'success':
                queue.compact()
                return [serialize_job(Job(id)) for id in queue.job_ids]
            else:
                return cls.successful_jobs()
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
        except Exception:
            pass
        return serialize_job(job)

    @classmethod
    def successful_jobs(cls):
        cls.connect()
        c = get_current_connection()
        jobs = c.keys('rq:job:*')
        sjobs = []
        for job in jobs:
            j = c.hgetall(job)
            if j.get('result'):
                key = job.replace('rq:job:','')
                sjobs.append(serialize_job(Job.fetch(key)))

        return sjobs


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
