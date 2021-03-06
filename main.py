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
import http.client
import urllib.parse
import json
import jwt
import datetime
from flask_api import FlaskAPI
from flask import jsonify, request
from flask_cors import CORS
from google.cloud import datastore
from data import scheme_dao, slab_dao, qp_def_dao, tx_dao, ws_dao, user_dao
from functools import wraps

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = FlaskAPI(__name__)
CORS(app)

app.config['GOOGLE_CLIENT_ID'] = '624703653577-qpuf27gt07fnqg1b6iu9f8q7ioslmos2.apps.googleusercontent.com'
app.config['GOOGLE_CLIENT_SECRET'] = 'Tntj5BbXGAazOs87CNuU2x_g'
app.config['APP_SECRET'] = 'tH1$_1$_4_$ECreT'


def provision_user(email):
  user = user_dao.add(email, email)
  user['workspaces'] = ws_dao.add_all(user['id'])
  return user


def token_required(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    token = None

    if 'x-access-token' in request.headers:
      token = request.headers['x-access-token']

    if not token:
      return {'message': 'Token is missing'}, 401

    try:
      data = jwt.decode(token, app.config['APP_SECRET'])
      current_user = user_dao.get_by_id(data['id'])
    except:
      return {'message': 'Token is invalid'}, 401

    return f(current_user, *args, **kwargs)
  return decorated

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
  slabs.sort(key=lambda i: i['lower_band'])
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


def calculate_tax(ws):

  scheme_id = ws['scheme_id']

  tx_list = tx_dao.get_by_ws_id(ws['id'])

  totals = {'in': 0, 'qp': 0, 'tp': 0}

  for tx in tx_list:
    totals[tx['type']] = totals[tx['type']] + tx['amt']

  qp_actual = get_qp(scheme_id, totals['in'], totals['qp'])

  i_rem = totals['in'] - qp_actual

  tax_total = 0
  taxable_total = 0

  slabs = slab_dao.get_by_scheme(scheme_id)
  slabs.sort(key=lambda i: i['lower_band'], reverse=True)

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

  slabs.sort(key=lambda i: i['lower_band'])

  calculation = {
    "scheme": scheme_id,
    "taxable_income": taxable_total,
    "qp_actual": qp_actual,
    "tax_total": tax_total - totals['qp'],
    "slabs": slabs}

  return calculation

# @app.route('/api/schemes/<scheme>/taxes')
# def get_tax(scheme):
#     income = request.args.get('in', type=float, default=0)
#     qp = request.args.get('qp', type=float, default=0)
#     tp = request.args.get('tp', type=float, default=0)

#     return calculate_tax(scheme,income,qp,tp);


@app.route('/api/ws/<int:ws_id>')
@token_required
def get_ws_info(user, ws_id):
  user_id = user['id']
  ws = ws_dao.get_by_id(user_id, ws_id)
  tx_list = tx_dao.get_by_ws_id(ws_id)
  totals = {'in': 0, 'qp': 0, 'tp': 0}

  for tx in tx_list:
    totals[tx['type']] = totals[tx['type']] + tx['amt']

  ws['transactions'] = tx_dao.get_by_ws_id(ws_id)
  ws['tax'] = calculate_tax(ws)

  return ws


@app.route('/api/ws/<int:ws_id>/taxes')
@token_required
def get_tax(user, ws_id):
  ws = ws_dao.get_by_id(user['id'], ws_id)

  return calculate_tax(ws)


def get_user_by_email(email):
  user = user_dao.get_by_email(email)

  if user == None:
    return provision_user(email)

  ws_list = ws_dao.get_by_user_id(user['id'])

  # for ws in ws_list:
  #     if ws['is_default'] == True:
  #         ws['transactions'] = tx_dao.get_by_ws_id(ws['id'])
  #         ws['tax'] = get_tax(user['id'], ws['id'])
  user['workspaces'] = ws_list

  return user


@app.route('/api/auth', methods=['POST'])
def auth():
  auth_code = request.json.get('code', None)

  if auth_code is None:
    return {'message': 'none'}

  params = {
    'code': auth_code,
    'client_id': app.config['GOOGLE_CLIENT_ID'],
    'client_secret': app.config['GOOGLE_CLIENT_SECRET'],
    'grant_type': 'authorization_code',
    'redirect_uri': 'http://localhost:3000'}

  json_payload = json.dumps(params)
  headers = {"Content-type": "application/json"}
  conn = http.client.HTTPSConnection('oauth2.googleapis.com')
  conn.request('POST', '/token', json_payload, headers)
  auth_response = conn.getresponse()
  auth_response_body = auth_response.read()
  conn.close()
  json_response = json.loads(auth_response_body)
  id_token = json_response['id_token']
  profile = jwt.decode(id_token, verify=False)
  user = get_user_by_email(profile['email'])
  user['picture'] = profile['picture']
  user['token'] = jwt.encode({
    'id': user.id,
    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
  }, app.config['APP_SECRET']).decode('UTF-8')
  return user

# ws


@app.route('/api/ws')
@token_required
def get_ws_by_user_id(user):
  return ws_dao.get_by_user_id(user['id'])

# tx


@app.route('/api/ws/<int:ws_id>/tx', methods=['GET'])
@token_required
def get_tx_by_ws_id(user, ws_id):
  tx_type = request.args.get('type')

  if tx_type == None:
    return tx_dao.get_by_ws_id(ws_id)
  else:
    return tx_dao.get_by_ws_id_type(ws_id, tx_type)


@app.route('/api/ws/<int:ws_id>/tx', methods=['POST'])
@token_required
def add_tx(user, ws_id):
  tx = request.json
  tx = tx_dao.add(ws_id, tx['type'], tx['date'], tx['desc'], tx['amt'])
  return tx, 201


@app.route('/api/ws/<int:ws_id>/tx/<int:id>', methods=['POST'])
@token_required
def update_tx(user, id, ws_id):
  tx = request.json
  tx_dao.update(id, ws_id, tx['type'], tx['date'], tx['desc'], tx['amt'])
  return tx


@app.route('/api/ws/<int:ws_id>/tx/<int:id>', methods=['DELETE'])
@token_required
def delete_tx(user, id, ws_id):
  tx_dao.delete(id, ws_id)
  return '', 200


if __name__ == '__main__':
  # This is used when running locally only. When deploying to Google App
  # Engine, a webserver process such as Gunicorn will serve the app. This
  # can be configured by adding an `entrypoint` to app.yaml.
  app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
