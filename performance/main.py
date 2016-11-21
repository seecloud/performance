# Copyright 2016: Mirantis Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import flask
import requests
import os
import json




app = flask.Flask(__name__)
es_url = ''
es_index_name = 'performance'
es_index_type = 'key_metrics'

@app.errorhandler(404)
def not_found(error):
    return flask.jsonify({"error": "Not Found"}), 404


def main():

    etcd_host = os.environ['ETCD_HOST']
    # For debug 
    pretty_js = lambda x: json.dumps(x, sort_keys=True, indent=4)   

    r = requests.get('http://' + etcd_host + ':2379/v2/keys/elasticsearch/endpoints/host')

    es_host = r.json()['node']['value']

    r = requests.get('http://' + etcd_host + ':2379/v2/keys/elasticsearch/endpoints/port')
    es_port = r.json()['node']['value']

    global es_url
    es_url = 'http://' + es_host + ':' + es_port 
    
    app.run(host=app.config.get("HOST", "0.0.0.0"),
            port=app.config.get("PORT", 5010))


# var1/var2/var3

#@app.route("/<region>/<metric>/<agg>")
#def get_health(region, metric, agg):
#
#    request_body =  {
#        'size': 0,
#            'query': {
#                'match': {
#                    'region': region
#                 }
#            },
#        'aggs': {
#            'agg_name': {
#                'filter' : { 'term': { 'metric': metric } },
#                'aggs' : { 'avg_value' : { agg : { "field" : "value" } } }
#            }
#        }
#    }
#
#
#    r = requests.post(es_url + "/_search?&pretty", json=request_body )
#
#    return flask.jsonify([r.json()])
#


#api/v1/region/<name_of_region>/performance/week
@app.route("/<region>/<metric>/<period>")
def get_health(region, metric, period):

    period_map = {
      'day':   'now-1d',
      'week':  'now-7d',
      'month': 'now-1M'
    }    
    
    interval_map = {
      'day':  '15m',
      'week': '100m',
      'month': '3100m'
    }
    
    request_body =  {
        "size": 0,
            "query": {
                "bool": {
                    "must": [
                     {
                         "range" : {
                         "timestamp" : {
                           "gte" : period_map[period],
                           "lt" :  "now",
                           "format" : "yyyy-MM-dd'T'H:m:s+00:00"
                }
            }
        },
        { "match": { "region": region }},
        { "match": { "metric": metric }}
        ]
        }
      },
      "aggs" : {
            "per_period" : {
                "date_histogram" : {
                    "field" : "timestamp",
                    "interval" : interval_map[period],
                    "format" : "yyyy-MM-dd'T'H:m:s+00:00",
                },
                "aggs": {
                    "extended_stats_agg": {
                        "extended_stats": {
                            "field": "value"
                        }
                    },
                    "percentiles_agg": {
                        "percentiles": {
                            "field": "value"
                        }
                    }
                }
            }
        },
    }
    
    
    r = requests.post(es_url + "/_search?&pretty", json=request_body )
    agg = r.json()['aggregations']['per_period']['buckets']
    return flask.jsonify([agg])
#    return flask.jsonify(r.json())



if __name__ == "__main__":
    main()
