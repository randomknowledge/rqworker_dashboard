import os
from time import sleep
from redis.client import Redis
from rq.connections import push_connection, get_current_connection
from django.conf import settings
from rq.queue import Queue

MODULE_DIR = os.path.dirname(__file__)
TEMPLATE_DIRS = getattr(settings, 'TEMPLATE_DIRS', ())
TEMPLATE_DIRS += (os.path.join(MODULE_DIR,'templates'),)
setattr(settings, 'TEMPLATE_DIRS', TEMPLATE_DIRS)

def setup_rq_connection():
    redis_conn = get_current_connection()
    if redis_conn == None:
        opts = getattr(settings, 'RQ_DASHBOARD_SETTINGS', {'db': 0, 'host': 'localhost', 'port': 6379})
        redis_conn = Redis(**opts)
        push_connection(redis_conn)

def enqueue(function, *args, **kwargs):
    setup_rq_connection()
    queue = kwargs.pop('queue', 'default')
    timeout = kwargs.pop('timeout', 3600)
    return Queue(queue).enqueue(function, *args, timeout=timeout, **kwargs)

def queueTestNormal( somarg, delay = 120 ):
    sleep(delay)

def queueTestFail( somarg, delay = 20 ):
    sleep(delay)
    raise Exception('Queue Test failed with arg "%s"!' % somearg)