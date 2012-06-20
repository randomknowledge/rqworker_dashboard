import logging
import os
from time import sleep
from django.utils import log
from redis.client import Redis
from rq.connections import push_connection, get_current_connection
from django.conf import settings
from rq.queue import Queue

logger  = logging.getLogger()

if not logger.handlers:
    logger.addHandler(log.NullHandler())

MODULE_DIR = os.path.dirname(__file__)

OPTIONS = getattr(settings, 'RQ_DASHBOARD_SETTINGS', {
    'poll_interval': 10,
    'remove_ghost_workers': True,
    'connection': {
        'db': 0,
        'host': 'localhost',
        'port': 6379
    }
})

def redis_runs_on_same_machine():
    host = OPTIONS.get('connection').get('host')
    return host == 'localhost' or host == '127.0.0.1'

def setup_rq_connection():
    redis_conn = get_current_connection()
    if redis_conn == None:
        opts = OPTIONS.get('connection')
        logger.debug('Establishing Redis connection to DB %(db)s at %(host)s:%(port)s' % opts)
        redis_conn = Redis(**opts)
        push_connection(redis_conn)

def enqueue(function, *args, **kwargs):
    setup_rq_connection()
    queue = kwargs.pop('queue', 'default')
    timeout = kwargs.pop('timeout', 3600)
    return Queue(queue).enqueue(function, *args, timeout=timeout, **kwargs)

def queueTestNormal( somarg, delay = 10 ):
    sleep(delay)
    return True

def queueTestFail( somarg, delay = 10 ):
    sleep(delay)
    raise Exception('Queue Test failed with arg "%s"!' % somearg)