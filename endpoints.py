from flask import request
from google.appengine.api import taskqueue
from vault import client, full_reload, renew_token
import logging

@app.route('/vault/refresh')
def vault_refresh():
    """
    Periodically called by cron.yaml

    This enqueues roughly one task a second that attempts to
    read from a location in Vault. Look in your GAE logs to
    confirm that you were/are able to read from Vault.
    """

    # There is a good deal of overlap here. This is done so that
    # we can be fairly certain that every second had one task
    # enqueued for it. I want a regular (no skipping) heartbeat.
    for i in range(120):
        # Right now
        d = datetime.now()
        # Right now + i seconds in the future
        d = datetime.timedelta(seconds=i)
        # Truncated to the second (so each second has unique task)
        d = d.replace(microsecond=0)
        taskqueue.add(url='/vault/beat',
                      name=d.isoformat().replace(':', '_'),
                      eta=d,
                      target='heartbeat')

    return "SUCCESS", 200

@app.route('/vault/beat')
def vault_refresh():
    """
    Task handler. Reads a value from Vault and confirms that the
    read value is the expected value.
    """

    r = vault.get('secret/canary')
    assert r['question'] = "What do you call a camel with 3 humps?"
    assert r['answer'] = "Pregnant!"

    return "SUCCESS", 200
