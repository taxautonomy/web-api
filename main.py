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
from flask import jsonify
from flask_cors import CORS
from google.cloud import datastore
from data import scheme_dao
from data import paye_slab_dao

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = FlaskAPI(__name__)
CORS(app)


# returns the slabs based on the tax scheme
@app.route('/api/paye/schemes')
def schemes():
    return scheme_dao.get_all()

def get_paye_calculation(scheme, salary):
    sal_remainder = salary
    tax_total = 0

    slabs = paye_slab_dao.get_by_scheme(scheme)
    slabs.sort(key = lambda i: i['lower_band'], reverse=True)

    for slab in slabs:
        amt = slab['lower_band']
        pct = slab['percentage']

        if sal_remainder > amt:
            taxable = sal_remainder - amt
            tax = taxable*pct/100
            sal_remainder = amt
            tax_total += tax
        else:
            taxable = 0
            tax = 0
        
        slab['taxable_amount'] = taxable
        slab['tax_calculated'] = tax

    slabs.sort(key = lambda i: i['lower_band'])

    calculation = {
        "scheme": scheme,
        "salary": salary,
        "tax_total": tax_total,
        "slabs": slabs}

    return calculation

@app.route('/api/paye/schemes/<scheme>/<int:salary>')
def paye(scheme, salary):
    return get_paye_calculation(scheme, salary)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
