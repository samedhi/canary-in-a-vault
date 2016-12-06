from google.appengine.ext import testbed, ndb
import main
import json
import subprocess
import unittest
import webtest


SECRET_CMD = 'vault write -f -field=secret_id auth/approle/role/app/secret-id'
ROLE_CMD = 'vault read -field=role_id auth/approle/role/app/role-id'


def init_vault(app):
    "This initializes the app using Vault (so that Vault.client works)"
    role_id = subprocess.check_output(ROLE_CMD.split(' '))
    secret_id = subprocess.check_output(SECRET_CMD.split(' '))
    js = {'role_id': role_id, 'secret_id': secret_id}
    app.post('/vault',
             json.dumps(js),
             content_type='application/json')


class AppTest(unittest.TestCase):

    def setUp(self):
        self.testapp = webtest.TestApp(main.app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_taskqueue_stub()
        init_vault(self.testapp)

    def tearDown(self):
        self.testbed.deactivate()

    def testEndpoints(self):
        self.testapp.get('/vault/refresh')

        self.testapp.post('/vault/beat')
