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
from flask import Flask
from flask import jsonify
from flask_cors import CORS
from google.cloud import datastore

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
CORS(app)


# returns the slabs based on the tax scheme


def query_paye_slabs(scheme):
    datastore_client = datastore.Client()

    # The kind for the new entity
    kind = 'paye-slab'
    # The name/ID for the new entity

    # The Cloud Datastore key for the new entity
    scheme_key = datastore_client.key('scheme', scheme)

    print("scheme key:{}".format(scheme_key.name))

    query1 = datastore_client.query(kind=kind, ancestor=scheme_key)
    #query1.add_filter('scheme', "=", scheme)
    return list(query1.fetch())
 
@app.route('/api/paye/<scheme>/<int:salary>')
def paye(scheme, salary):
    tax_slabs = []
    sal_remainder = salary

    app.logger.info('Scheme: %s', scheme)
    app.logger.info('Salary: %d', salary)
    tax_total = 0

    slabs = query_paye_slabs(scheme)

    for i in range(len(slabs)):
        j = len(slabs) - i - 1
        amt = slabs[j]['lower_band']
        pct = slabs[j]['percentage']

        if sal_remainder > amt:
            taxable = sal_remainder - amt
            tax = taxable*pct/100
            sal_remainder = amt
            tax_total += tax
        else:
            taxable = 0
            tax = 0

        tax_slab = {
            "lower_band": amt,
            "percentage": pct,
            "taxable_amount": taxable,
            "tax_calculated": tax
        }
        tax_slabs.append(tax_slab)

    calculation = {
        "salary": salary,
        "tax_total": tax_total,
        "slabs": tax_slabs}

    return jsonify(calculation)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
