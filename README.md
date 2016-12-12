# Canary in a Vault

## Purpose

This project exist to act as a sort of [Canary in a Coal Mine](https://en.wikipedia.org/wiki/Sentinel_species) for [Vault](https://www.vaultproject.io/). It is a Google App Engine application whose only purpose is to request a key from Vault once a second. By looking at your logs, you can easily confirm that Vault is up and available.

## Additional Resources
* [Get A Vault Token to your application](http://samedhi.github.io/code/2016/12/11/get-a-vault-token-to-your-application.html)

## Setup

### Vault Server

You need to have a running Vault server. Vault is serious about security, so your server will need to have a valid cert and be served over SSL. Be sure to place the domain of your Vault server [here](https://github.com/samedhi/canary-in-a-vault/blob/master/vault.py#L13).

From this point on your Vault server will be referred to as `<VAULT_SERVER>`

### Vault Client
1. You need to have the [Vault Command Line ](https://www.vaultproject.io/docs/install/install.html) on your local machine.
2. Auth with your Vault server.
3. Enter the following, be sure to replace `<YOUR_SUPER_SECRET_BEARER_TOKEN>`
```bash
$ vault write secret/canary \
  question="What do you call a camel with 3 humps?" \
  answer="Pregnant" \
  bearer_token="<YOUR_SUPER_SECRET_BEARER_TOKEN>"
```

TODO: role_id is your bearer token.

### Google App Engine
You need to install the [gcloud sdk](https://cloud.google.com/sdk/downloads). Once that is done go to the [Google Console](https://console.cloud.google.com/) and create a new project. We will call the `project-id` of your newly project `PROJECT_ID`.

### This Project
Clone and enter this project. You need to `pip install` some additional dependencies that GAE does not provide.
```bash
$ git clone git@github.com:samedhi/canary-in-a-vault.git
$ cd canary-in-a-vault
$ pip install --ignore-installed --target=lib -r requirements.txt
```

## Test

```bash
$ echo $GOOGLE_CLOUD_SDK
/Users/stephen/Bin/google-cloud-sdk/
$ python runner.py $GOOGLE_CLOUD_SDK
```

## Deploy
### 1) Deploy the app:
```bash
$ gcloud app deploy app.yaml cron.yaml --project <PROJECT-ID>
```
### 2) Light the pilot Light
Assuming an application named `<APP>`, you might enter the following to pass a `role_id` and `secret_id` to Vault. Don't forget to replace replace `<APP>` with the actual Vault name of your application!
```bash
$ curl \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(vault read -field=bearer_token secret/canary)" \
  -d "{\"role_id\": \
       \"$(vault read -field=role_id <APP>/approle/role/app/role-id)\", \
       \"secret_id\": \
       \"$(vault write -f -field=secret_id <APP>/approle/role/app/secret-id)\"}" \
    <VAULT_SERVER>
```
