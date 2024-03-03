import hvac
import os

def get_secrets(vault_address):
  client = hvac.Client(
          url=vault_address
          )
  
  client.auth.approle.login(
      role_id=os.environ['ROLE_ID'],
      secret_id=os.environ['SECRET_ID'],
  )
  
  secrets = client.secrets.kv.v2.read_secret(path='detector')
  return secrets