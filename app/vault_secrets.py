import hvac
import os

def get_secrets(vault_address):
  client = hvac.Client(
          url=vault_address,
        cert=('/app/cert.pem', '/app/key.pem')
        )
  client.auth.cert.login()
  secrets = client.secrets.kv.v2.read_secret(path='detector')
  return secrets