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
from flask import Flask
from flask import jsonify


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

import sys

# returns the slabs based on the tax scheme
def get_slabs(scheme_name):
    if scheme_name == "2018-2019":
        return [[0,0],
            [100000,4],
            [150000,8],
            [200000,12],
            [250000,16],
            [300000,20],
            [350000,24]]
    elif scheme_name == "2019-2020":
        return [[0,0],
            [250000,6],
            [500000,12],
            [750000,18]]
    else:
        return [[0,0]]

@app.route('/api/paye/<scheme>/<int:salary>')
def paye(scheme, salary):
    tax_slabs = []
    sal_remainder = salary

    app.logger.info('Scheme: %s', scheme)
    app.logger.info('Salary: %d', salary)
    tax_total = 0

    slabs = get_slabs(scheme)

    for i in range(len(slabs)):
        j = len(slabs) - i - 1
        amt=slabs[j][0]
        pct=slabs[j][1]

        if sal_remainder > amt:
            taxable = sal_remainder - amt
            tax = taxable*pct/100
            sal_remainder = amt
            tax_total += tax
        else:
            taxable=0
            tax=0

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
