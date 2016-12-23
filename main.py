from datetime import datetime, timedelta
from flask import Flask, request
from google.appengine.api import taskqueue, memcache
from jinja2 import Environment, FileSystemLoader
import logging
import vault


app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/vault', methods=['POST'])
def post_vault():
    """
    Record our vault token in the Datastore.

    REQUEST Body (as JSON):
    {
    'role_id': <String>,         # "xxxx-abcd-1234"
    'secret_id': <String>,       # "xxxx-secretz-1234"
    }

    200 RESPONSE on Success
    """
    r = request.get_json()
    vault.init(r['role_id'], r['secret_id'])
    return "SUCCESS", 200


@app.route('/vault/refresh')
def vault_refresh():
    """
    Periodically called by cron.yaml

    This enqueues roughly one task a second that attempts to
    read from a location in Vault. Look in your GAE logs to
    confirm that you were/are able to read from Vault.

    This also extends the lifetime of the client's token to
    now() + N Minutes (specified in token).
    """
    vault.renew_token()

    # Right now
    now = datetime.now()

    # There is a good deal of overlap here. This is done so that
    # we can be fairly certain that every second had one task
    # enqueued for it. I want a regular (no skipping) heartbeat.
    for i in range(120):
        # Right now + i seconds in the future
        d = now + timedelta(seconds=i)
        # Truncated to the second (so each second has unique task)
        d = d.replace(microsecond=0)
        try:
            taskqueue.add(url='/vault/beat',
                          name=d.isoformat().replace(':', '_'),
                          eta=d)
        except BaseException as e:
            pass

    return "SUCCESS", 200


# The math on all of this is not strictly correct, but it is
# "eyeball good". If you need real metrics for errors and
# latency, you should be looking at logs or elasticsearch.

def cas_fx(k, fx):
    i = 0
    client = memcache.Client()
    while i < 3:
        i = i + 1
        avg_value = client.gets(k)
        if avg_value is None:
            memcache.add(k, 0)
            continue
        new_avg = fx(avg_value)
        if client.cas(k, new_avg):
            break


def record_success(start):
    end = datetime.now()
    s = (end - start).total_seconds()
    cas_fx('LATENCY_DAY_' + end.strftime('%Y-%m-%d'),
           lambda avg: avg + s / (60 * 60 * 24))
    cas_fx('LATENCY_HOUR_' + end.strftime('%Y-%m-%d-%H'),
           lambda avg: avg + s / (60 * 60))
    cas_fx('LATENCY_MINUTE_' + end.strftime('%Y-%m-%d-%H-%M'),
           lambda avg: avg + s / 60)


def record_failure(start):
    memcache.set('LAST_FAILURE', start)


@app.route('/vault/beat', methods=['POST'])
def vault_beat():
    """
    Task handler. Reads a value from Vault and confirms that the
    read value is the expected value.
    """
    now = datetime.now()
    try:
        r = vault.get('secret/canary')
        record_success(now)
    except BaseException as e:
        # record_failure(now)
        logging.exception(e)
        return "VAULT FAILURE", 205

    try:
        assert r['question'] == "What do you call a camel with 3 humps?", r
        assert r['answer'] == "Pregnant", r
    except BaseException as e:
        logging.exception(e)
        return "LOGIC FAILURE", 210

    return "SUCCESS", 200

env = Environment(loader=FileSystemLoader('templates'))

@app.route('/')
def vault_summary():
    """
    Analytics about how things are doing.
    """
    t = env.get_template('summary.html')
    return t.render(active_days=1,
                    active_hours=1,
                    active_minutes=1,
                    active_seconds=1,
                    latency_day=1.2345,
                    latency_hour=1.234,
                    latency_minute=1.23)
