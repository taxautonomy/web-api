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

def insert_scheme(assessment_year):
    # [START datastore_quickstart]
    # Imports the Google Cloud client library

    # Instantiates a client

    # The kind for the new entity
    kind = 'scheme'
    # The name/ID for the new entity

    # The Cloud Datastore key for the new entity
    scheme_key = datastore_client.key(kind, assessment_year)

    # Prepares the new entity
    scheme = datastore.Entity(key=scheme_key)
    scheme['assessment_year'] = assessment_year

    # Saves the entity
    datastore_client.put(scheme)

    print('Saved {}: {}'.format(scheme.key, scheme['assessment_year']))
    # [END datastore_quickstart]

def insert_paye_slab(scheme, lower_band, percentage):


    # The kind for the new entity
    kind = 'paye-slab'
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

def query_paye_slabs(scheme):

    # The kind for the new entity
    kind = 'paye-slab'
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
        print(s['assessment_year'])

if __name__ == '__main__':
    get_schemes()
    insert_scheme('2018-2019')
    insert_scheme('2019-2020')
    insert_paye_slab('2019-2020', 250000, 6)
    insert_paye_slab('2019-2020', 500000, 12)
    insert_paye_slab('2019-2020', 750000, 18)
    insert_paye_slab('2018-2019', 100000, 4)
    insert_paye_slab('2018-2019', 150000, 8)
    insert_paye_slab('2018-2019', 200000, 12)
    insert_paye_slab('2018-2019', 250000, 16)
    insert_paye_slab('2018-2019', 300000, 20)
    insert_paye_slab('2018-2019', 350000, 24)