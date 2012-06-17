from redis.client import Redis
from rq.connections import push_connection, get_current_connection
from django.conf import settings

def setup_rq_connection():
    redis_conn = get_current_connection()
    if redis_conn == None:
        opts = getattr(settings, 'RQ_DASHBOARD_SETTINGS', {'db': 0, 'host': 'localhost', 'port': 6379})
        redis_conn = Redis(**opts)
        push_connection(redis_conn)
