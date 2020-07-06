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

def update(id, ws_id, tx_type, date, desc, amt):
    with db.transaction():
        ws_key = db.key('ws', ws_id)
        tx_key = db.key(KIND, id, parent=ws_key)
        tx = db.get(tx_key)
        # tx = datastore.Entity(tx_key, id)
        tx.update({
            'date':date,
            'desc':desc,
            'amt':amt
        })

        db.put(tx)

def delete(id, ws_id):
    ws_key = db.key('ws', ws_id)
    tx_key = db.key(KIND, id, parent=ws_key)
    db.delete(tx_key)

def build_resultset(rawdata):
    results = list(rawdata)
    for tx in results:
        tx['id'] = tx.key.id
    return results

def get_by_ws_id(ws_id):
    ws_key = db.key('ws', ws_id)
    get_tx_query = db.query(kind=KIND, ancestor=ws_key)
    return build_resultset(get_tx_query.fetch())

def get_by_ws_id_type(ws_id, tx_type):
    ws_key = db.key('ws', ws_id)
    get_tx_query = db.query(kind=KIND, ancestor = ws_key)
    get_tx_query.add_filter('type', '=', tx_type)
    return build_resultset(get_tx_query.fetch())
