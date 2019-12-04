
from google.cloud import datastore

def get_all():
    datastore_client = datastore.Client()
    kind = 'scheme'
    get_schemes_query = datastore_client.query(kind=kind)
    return list(get_schemes_query.fetch())