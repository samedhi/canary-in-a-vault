import json
import subprocess
import vault

SECRET_CMD = 'vault write -f -field=secret_id auth/approle/role/app/secret-id'
ROLE_CMD = 'vault read -field=role_id auth/approle/role/app/role-id'
ROLE_ID = subprocess.check_output(ROLE_CMD.split(' '))
SECRET_ID = subprocess.check_output(SECRET_CMD.split(' '))
CLIENT_TOKEN = vault.client.auth_approle(ROLE_ID, SECRET_ID)['auth']['client_token']

def init(app):
    "This initializes the app using Vault (so that Vault.client works)"
    app.post('/vault',
             json.dumps({'role_id': ROLE_ID,
                         'secret_id': SECRET_ID}),
             content_type='application/json')
