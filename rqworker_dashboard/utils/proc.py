import psutil
from psutil.error import NoSuchProcess
from .. import redis_runs_on_same_machine, OPTIONS, setup_rq_connection
from log import logger
from rq.worker import Worker


def worker_running(worker):
    _, _, realpid = worker.key.partition('.')
    try:
        psutil.Process(int(realpid))
    except NoSuchProcess:
        return False
    else:
        return True


def remove_ghost_workers():
    if not OPTIONS.get('remove_ghost_workers', False):
        return

    if not redis_runs_on_same_machine():
        logger.warning('Cannot remove Ghost Workers, because the configured Redis Server is not running on localhost!')
        return

    setup_rq_connection()

    for w in Worker.all():
        if not worker_running(w):
            w.register_death()