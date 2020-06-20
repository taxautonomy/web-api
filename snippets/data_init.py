#!/usr/bin/env python

# Copyright 2016 Google Inc. All Rights Reserved.
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
from google.cloud import datastore

datastore_client = datastore.Client()

def insert_scheme(id, assessment_year, scheme_type, scheme_name):
    # [START datastore_quickstart]
    # Imports the Google Cloud client library

    # Instantiates a client

    # The kind for the new entity
    kind = 'scheme'
    # The name/ID for the new entity

    # The Cloud Datastore key for the new entity
    scheme_key = datastore_client.key(kind, id)

    # Prepares the new entity
    scheme = datastore.Entity(key=scheme_key)
    scheme['year'] = assessment_year
    scheme['type'] = scheme_type
    scheme['name'] = scheme_name

    # Saves the entity
    datastore_client.put(scheme)

    print('Saved {}: {}'.format(scheme.key, scheme))
    # [END datastore_quickstart]

def insert_slab(scheme, lower_band, percentage):

    # The kind for the new entity
    kind = 'slab'
    # The name/ID for the new entity

    # The Cloud Datastore key for the new entity
    scheme_key = datastore_client.key('scheme', scheme)
    print("scheme key:{}".format(scheme_key.name))
    slab_key = datastore_client.key(kind, lower_band, parent=scheme_key)

    # Prepares the new entity
    slab = datastore.Entity(key=slab_key)
    #slab['scheme'] = scheme
    slab['lower_band'] = lower_band
    slab['percentage'] = percentage

    # Saves the entity
    datastore_client.put(slab)

    print('Saved {}: {}'.format(slab.key, slab['lower_band']))
    # [END datastore_quickstart]

def query_slabs(scheme):

    # The kind for the new entity
    kind = 'slab'
    # The name/ID for the new entity

    # The Cloud Datastore key for the new entity
    scheme_key = datastore_client.key('scheme', scheme)

    print("scheme key:{}".format(scheme_key.name))

    query1 = datastore_client.query(kind=kind, ancestor=scheme_key)
    #query1.add_filter('scheme', "=", scheme)
    slabs = list(query1.fetch())
    for s in slabs:
        print("Lower Band: LKR {}, Percentage: {}%".format(s["lower_band"], s["percentage"]))
    # [END datastore_quickstart]

def insert_qp_def(scheme, id, name, cap):

    # The kind for the new entity
    kind = 'qp-def'
    # The name/ID for the new entity

    # The Cloud Datastore key for the new entity
    scheme_key = datastore_client.key('scheme', scheme)
    print("scheme key:{}".format(scheme_key.name))
    qp_key = datastore_client.key(kind, id, parent=scheme_key)

    # Prepares the new entity
    qp = datastore.Entity(key=qp_key)
    #slab['scheme'] = scheme
    qp['name'] = name
    qp['cap'] = cap

    # Saves the entity
    datastore_client.put(qp)

    print('Saved {}: {}'.format(qp.key, qp['name']))
    # [END datastore_quickstart]

def get_schemes():
        # The kind for the new entity
    kind = 'scheme'
    # The name/ID for the new entity

    # The Cloud Datastore key for the new entity
    #scheme_key = datastore_client.key('scheme', scheme)

    #print("scheme key:{}".format(scheme_key.name))

    get_schemes_query = datastore_client.query(kind=kind)
    #query1.add_filter('scheme', "=", scheme)
    schemes = list(get_schemes_query.fetch())
    for s in schemes:
        print(s['name'])

if __name__ == '__main__':
    get_schemes()
    #insert_scheme('2019-2020-personal-new','2019-2020','personal', '2019/20 (NEW) - Personal')
    #insert_scheme('2020-2021-personal', '2020-2021','personal','2020/21 - Personal')
    # insert_slab('2019-2020-personal-new',  750000, 6)
    # insert_slab('2019-2020-personal-new', 1500000, 12)
    # insert_slab('2019-2020-personal-new', 2250000, 18)
    # insert_slab('2020-2021-personal', 3000000, 6)
    # insert_slab('2020-2021-personal', 6000000, 12)
    # insert_slab('2020-2021-personal', 9000000, 18)
    # query_slabs('2019-2020-personal-new')
    # query_slabs('2020-2021-personal')
    insert_qp_def('2019-2020-personal-new','general','General Qualifying Payments', 1200000)