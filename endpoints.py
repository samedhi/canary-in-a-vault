from flask import request
from google.appengine.api import taskqueue
from vault import client, full_reload, renew_token
import logging


def singleton_key():
    return ndb.Key('Vault', 'SINGLETON')


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
    # We need to go to vault to exchange our
    # (vault_key(), VAULT_SECRET) for a token. We then
    # save all of this permanently in Datastore.
    response = client.auth_approle(r['role_id'], r['secret_id'])
    auth = response['auth']
    client.token = auth['client_token']
    v = Vault(key=singleton_key(), # key is fixed (Singleton)
              role_id=r['role_id'],
              token=client.token)
    v.put()
    return "SUCCESS", 200


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
