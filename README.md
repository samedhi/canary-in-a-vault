# Canary in a Vault

## Purpose

This project exist to act as a sort of "canary in the coalmine" for Vault. It is an Google App Engine application whose only purpose is to request a key from Vault once a second. By looking at your logs, you can easily confirm that Vault is up and available.

## Setup

1. You need to have a running Vault server with a valid cert. Be sure to place the domain of your IP address ![here](https://github.com/samedhi/canary-in-a-vault/blob/master/vault.py#L13) in order to connect to your Vault server.
2. You need to have vault installed on your local machine.
3. You need to install some app engine depencies into your local `/lib` directory.
```
> git clone git@github.com:samedhi/canary-in-a-vault.git
> cd canary-in-a-vault
> pip install --ignore-installed --target=lib -r requirements.txt
```

## Test

```
> python runner.py $GOOGLE_CLOUD_SDK
```

## Deploy
