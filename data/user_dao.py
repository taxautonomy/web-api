from google.cloud import datastore

KIND = 'user'
db = datastore.Client()

def add(email, name):
    user_key = db.key(KIND)
    user = datastore.Entity(key=user_key)
    # user['email'] = email
    # user['name'] = name
    user.update({
        'email': email,
        'name': name
    })

    db.put(user)
    user['id'] = user.key.id
    return user

def get_by_email(email):
    get_user_query = db.query(kind=KIND)
    get_user_query.add_filter('email', '=', email)
    result = list(get_user_query.fetch())
    if len(result) >= 1:
        user = result[0]
        user['id'] = user.key.id
        return user
    return None