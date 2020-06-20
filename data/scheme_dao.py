
from google.cloud import datastore

def get_all():
    datastore_client = datastore.Client()
    kind = 'scheme'
    get_schemes_query = datastore_client.query(kind=kind)
    return list(get_schemes_query.fetch())

def get_by_id(id):
    datastore_client = datastore.Client()
    scheme_key = datastore_client.key('scheme', id)
    print(scheme_key)
    scheme = datastore_client.get(scheme_key)
    print(scheme)
    return scheme