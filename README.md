# Canary in a Vault

## Purpose

This project exist to act as a sort of "canary in the coalmine" for Vault. It is a Google App Engine application whose only purpose is to request a key from Vault once a second. By looking at your logs, you can easily confirm that Vault is up and available.

## Setup

# Vault Server

You need to have a running Vault server with a valid cert. Be sure to place the domain of your Vault server [here](https://github.com/samedhi/canary-in-a-vault/blob/master/vault.py#L13).
# Vault Local 
You need to have [Vault installed](https://www.vaultproject.io/docs/install/install.html) on your local machine.
# Pip
You need to `pip install` some app engine depencies into your local `/lib` directory.
```
> git clone git@github.com:samedhi/canary-in-a-vault.git
> cd canary-in-a-vault
> pip install --ignore-installed --target=lib -r requirements.txt
```
# Setup a Secret 
You need to put something to look up in Vault.
```
> vault write secret/canary question="What do you call a camel with 3 humps?" answer="Pregnant"
```

## Test

```
> python runner.py $GOOGLE_CLOUD_SDK
```

## Deploy
