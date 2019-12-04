from google.cloud import datastore

def get_by_scheme(scheme):
    datastore_client = datastore.Client()

    # The kind for the new entity
    kind = 'paye-slab'
    # The name/ID for the new entity

    # The Cloud Datastore key for the new entity
    scheme_key = datastore_client.key('scheme', scheme)
    get_slabs_query = datastore_client.query(kind=kind, ancestor=scheme_key)
    return list(get_slabs_query.fetch())