`rqworker_dashboard` is a django app that provides a simple dashboard for [RQ](https://github.com/nvie/rq).
Inspired by [rq-dashboard](https://github.com/nvie/rq-dashboard)

## Installing

Download source and install package using pip:

```console
$ pip install -e git+https://github.com/randomknowledge/rqworker_dashboard.git#egg=rqworker_dashboard
```


Add this to your project's `settings.py`.
Those are also the default settings.

```python
RQ_DASHBOARD_SETTINGS = {
    'poll_interval': 10,
    'connection': {
        'db': 0,
        'host': 'localhost',
        'port': 6379
    }
}
```


Add this to your project's `urls.py`:

```python
url(r'^admin/rq/', include('rqworker_dashboard.urls')),
```

### Login to django admin and point your browser to [http://your.server/admin/rq/](http://your.server/admin/rq/)