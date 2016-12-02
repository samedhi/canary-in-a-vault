from datetime import datetime
from flask import request
from google.appengine.ext import ndb
import hvac
import json
import logging
import models
import os


# https://gist.github.com/TheKevJames/22e1e6c3545a758171013440bf587b12
from urlparse import urljoin
import requests
def auth_approle(self, role_id, secret_id):
    url = urljoin(self._url, '/v1/auth/approle/login')
    params = {
        'role_id': role_id,
        'secret_id': secret_id,
    }

    response = self.session.post(url, allow_redirects=False, json=params, **self._kwargs)
    while response.is_redirect:
        self.session = requests.Session()
        self.session.headers['hostname'] = 'vault.talkiq.net'
        response = self.session.post(url, allow_redirects=False, json=params, **self._kwargs)
    return response.json()

hvac.Client.auth_approle = auth_approle
# END

VAULT_DOMAIN = 'vault.talkiq.net'

VAULT_ADDR = 'https://%s:8200'

client = None

def reload_client():
    "Sets up the `client` connection to Vault"
    global client
    session = requests.Session()
    session.headers['hostname'] = VAULT_DOMAIN
    client = hvac.Client(url=VAULT_ADDR, session=session)

def refresh_token():
    "Ensures this instances' client has the newest Vault token"
    token = singleton_key().get().token
    assert token
    if client.token != token:
        logging.info("Token changed! %s => %s", client.token, token)
        client.token = token

def renew_token():
    "Extends the expiration time on client.token"
    if client.token:
        client.renew_token()

def full_reload():
    logging.info("Attempting to reload vault.client")
    reload_client()
    refresh_token()
    logging.info("Finished reloading vault.client")

def get(path):
    "Get the Vault dictionary at path"
    # clean up ambiguous paths
    # '/a/b/', '/a/b', 'a/b', 'a/b/' all become 'a/b'
    path = '/'.join(filter(lambda s: s.strip(),path.split('/')))
    i = 0
    while i < 3:
        try:
            v_data = client.read(path)['data']
            break
        except BaseException as e:
            i = i + 1
            if i >= 3:
                logging.error("Persistent Vault Failure path=`%s` return=`%s`", path, c_data)
                break
            logging.warning("Vault Failed")
            logging.exception(e)
            logging.warning(client.session.headers)
            full_reload()

# kickstart `client` being initialized before this module finishes loading
reload_client()
