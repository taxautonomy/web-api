#! /usr/bin/python3
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python37_app]

import sys
from flask_api import FlaskAPI
from flask import jsonify, request
from flask_cors import CORS
from google.cloud import datastore
from data import scheme_dao, slab_dao, qp_def_dao, tx_dao, ws_dao, user_dao

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = FlaskAPI(__name__)
CORS(app)


# returns the slabs based on the tax scheme
@app.route('/api/schemes')
def get_schemes():
    scheme_list = scheme_dao.get_all()
    return scheme_list

@app.route('/api/schemes/<scheme_id>')
def get_scheme(scheme_id):
    scheme = scheme_dao.get_by_id(scheme_id)
    scheme['slabs'] = get_slabs_by_scheme(scheme_id)
    scheme['qp_def'] = qp_def_dao.get_by_scheme(scheme_id)
    return scheme

@app.route('/api/schemes/<scheme_id>/slabs')
def get_slabs_by_scheme(scheme_id):
    slabs = slab_dao.get_by_scheme(scheme_id)
    slabs.sort(key = lambda i: i['lower_band'])
    return slabs

@app.route('/api/schemes/<scheme_id>/qp_def')
def get_qp_def(scheme_id):
    return qp_def_dao.get_by_scheme(scheme_id)

def get_qp(scheme, income, qp_supplied):
    qp_def_list = qp_def_dao.get_by_scheme(scheme)
    if len(qp_def_list) == 0:
        return 0
    
    qp_cap = qp_def_list[0]['cap']

    return qp_supplied if qp_supplied < qp_cap else qp_cap

def calculate_tax(scheme, income, qp, tp):

    qp_actual = get_qp(scheme, income, qp)
    
    i_rem = income - qp_actual

    tax_total = 0
    taxable_total = 0

    slabs = slab_dao.get_by_scheme(scheme)
    slabs.sort(key = lambda i: i['lower_band'], reverse=True)

    for slab in slabs:
        amt = slab['lower_band']
        pct = slab['percentage']

        if i_rem > amt:
            taxable = i_rem - amt
            tax = taxable*pct/100
            i_rem = amt
            tax_total += tax
        else:
            taxable = 0
            tax = 0
        
        taxable_total += taxable
        slab['taxable_amount'] = taxable
        slab['tax_calculated'] = tax

    slabs.sort(key = lambda i: i['lower_band'])

    calculation = {
        "scheme": scheme,
        "taxable_income": taxable_total,
        "qp_actual": qp_actual,
        "tax_total": tax_total - tp,
        "slabs": slabs}

    return calculation

@app.route('/api/schemes/<scheme>/taxes')
def get_tax(scheme):
    income = request.args.get('in', type=float, default=0)
    qp = request.args.get('qp', type=float, default=0)
    tp = request.args.get('tp', type=float, default=0)

    return calculate_tax(scheme,income,qp,tp)

# user
@app.route('/api/users')
def get_user_by_email():
    email = request.args.get('email')
    user = user_dao.get_by_email(email)
    user['workspaces'] = ws_dao.get_by_user_id(user['id'])
    if user == None:
        return '', 404
    return user

# ws
@app.route('/api/users/<user_id>/ws')
def get_ws_by_user_id(user_id):
    return ws_dao.get_by_user_id(int(user_id))

# tx
@app.route('/api/ws/<ws_id>/tx', methods=['GET'])
def get_tx_by_ws_id(ws_id):
    tx_type = request.args.get('type')

    if tx_type == None:
        return tx_dao.get_by_ws_id(int(ws_id))
    else:
        return tx_dao.get_by_ws_id_type(int(ws_id), tx_type)

@app.route('/api/ws/<ws_id>/tx', methods=['POST'])
def add_tx(ws_id):
    tx = request.json
    tx_dao.add(int(ws_id), tx['type'], tx['date'], tx['desc'], tx['amt'])
    return tx, 201

@app.route('/api/ws/<ws_id>/tx/<id>', methods=['POST'])
def update_tx(id, ws_id):
    tx = request.json
    tx_dao.update(int(id), int(ws_id), tx['type'], tx['date'], tx['desc'], tx['amt'])
    return tx

@app.route('/api/ws/<ws_id>/tx/<id>', methods=['DELETE'])
def delete_tx(id, ws_id):
    tx_dao.delete(int(id), int(ws_id))
    return '', 200

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
