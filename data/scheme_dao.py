from google.cloud import datastore
from collections import defaultdict

def get_all():
  datastore_client = datastore.Client()
  kind = 'scheme'
  get_schemes_query = datastore_client.query(kind=kind)
  schemes = list(get_schemes_query.fetch())

  for scheme in schemes:
    scheme['id'] = scheme.key.name
      
  return schemes

def get_by_id(id):
  datastore_client = datastore.Client()
  scheme_key = datastore_client.key('scheme', id)
  scheme = datastore_client.get(scheme_key)
  return scheme