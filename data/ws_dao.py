from google.cloud import datastore
from data import scheme_dao

KIND = 'ws'
db = datastore.Client()

def add(user_id, scheme_id, scheme_type, scheme_name, is_active, is_default):

    user_key = db.key('user', user_id)
    ws_key = db.key(KIND, parent=user_key)
    ws = datastore.Entity(key=ws_key)

    ws.update({
        'user_id': user_id,
        'scheme_id': scheme_id,
        'type': scheme_type,
        'name':scheme_name,
        'is_active':is_active,
        'is_default':is_default
    })

    db.put(ws)

def get_by_user_id(user_id):
    user_key = db.key('user', user_id)
    get_ws_query = db.query(kind=KIND, ancestor=user_key)
    result = list(get_ws_query.fetch())
    for ws in result:
        ws['id'] = ws.key.id
    return result 

def add_all(user_id):
    schemes = scheme_dao.get_all()
    for scheme in schemes:
        add(user_id, scheme['id'], scheme['type'], scheme['name'], scheme['is_active'], scheme['is_default'])
