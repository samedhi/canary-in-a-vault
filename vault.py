from datetime import datetime
from flask import request
from google.appengine.ext import ndb
from requests_toolbelt.adapters import host_header_ssl
from urlparse import urljoin
import hvac
import json
import logging
import os
import requests


VAULT_DOMAIN = 'vault.talkiq.net' # <- Put your DOMAIN here

VAULT_ADDR = 'https://%s:8200' % VAULT_DOMAIN

client = None

class Vault(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    role_id = ndb.StringProperty()
    token = ndb.StringProperty()


def singleton_key():
    return ndb.Key('Vault', 'SINGLETON')


def init(role_id, secret_id):
    """
    Go to to Vault to exchange our role_id and secret_id for a
    token. We then save all of this permanently in Datastore.
    """
    try:
        response = client.auth_approle(role_id, secret_id)
        auth = response['auth']
        client_token = auth['client_token']
        v = Vault(key=singleton_key(), # key is fixed (Singleton)
                  role_id=role_id,
                  token=client_token)
        v.put()
        client.token = client_token
    except BaseException:
        logging.error("Failed to update token with %s %s", role_id, secret_id)
        raise

def build_client():
    "Sets up the `client` connection to Vault"
    global client
    client = hvac.Client(url=VAULT_ADDR)
    client.session.mount('https://', host_header_ssl.HostHeaderSSLAdapter())
    client.session.headers['Host'] = VAULT_DOMAIN


# kickstart `client` being initialized before this module finishes loading
build_client()


def load_token():
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
    build_client()
    load_token()


def get(path):
    "Get the Vault dictionary at path"
    # clean up ambiguous paths
    # '/a/b/', '/a/b', 'a/b', 'a/b/' all become 'a/b'
    path = '/'.join(filter(lambda s: s.strip(),path.split('/')))
    i = 0
    while i < 3:
        try:
            return client.read(path)['data']
        except BaseException as e:
            if i >= 1:
                logging.error("Persistent Vault Failure on path=`%s", path)
                raise
            i = i + 1
            logging.warning("Vault Failure %s" % i)
            logging.exception(e)
            full_reload()
