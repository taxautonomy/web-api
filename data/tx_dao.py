from google.cloud import datastore

KIND = 'tx'
db = datastore.Client()

def add(ws_id, tx_type, date, desc, amt):
    ws_key = db.key('ws', ws_id)
    tx_key = db.key(KIND, parent=ws_key)
    tx = datastore.Entity(key=tx_key)
    tx.update({
        'ws_id':ws_id,
        'type':tx_type,
        'date':date,
        'desc':desc,
        'amt':amt
    })

    db.put(tx)

def get_by_ws_id(ws_id):
    ws_key = db.key('ws', ws_id)
    get_tx_query = db.query(kind=KIND, ancestor=ws_key)
    return list(get_tx_query.fetch())

def get_by_ws_id_type(ws_id, tx_type):
    ws_key = db.key('ws', ws_id)
    get_tx_query = db.query(kind=KIND, ancestor = ws_key)
    get_tx_query.add_filter('type', '=', tx_type)
    return list(get_tx_query.fetch()) 