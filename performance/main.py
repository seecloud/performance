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
import six
import json

app = flask.Flask(__name__)
es_url = ''
es_index_name = 'performance'
es_index_type = 'key_metrics'

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

pretty_js = lambda x: json.dumps(x, sort_keys=True, indent=4)


@app.errorhandler(404)
def not_found(error):
    return flask.jsonify({"error": "Not Found"}), 404


def main():

    etcd_host = os.environ['ETCD_HOST']

    r = requests.get('http://' + etcd_host +
                     ':2379/v2/keys/elasticsearch/endpoints/host')

    es_host = r.json()['node']['value']

    r = requests.get('http://' + etcd_host +
                     ':2379/v2/keys/elasticsearch/endpoints/port')
    es_port = r.json()['node']['value']

    global es_url
    es_url = 'http://' + es_host + ':' + es_port

    app.run(host=app.config.get("HOST", "0.0.0.0"),
            port=app.config.get("PORT", 5010))


@app.route("/api/v1/performance/<period>")
def get_perf(period):
    request_body = {
        "size": 0,
        "query": {
            "bool": {
                "must": [{
                    "range": {
                        "timestamp": {
                            "gte": period_map[period],
                            "lt":  "now",
                            "format": "yyyy-MM-dd'T'H:m:s+00:00"
                        }
                    }
                }]
            }
        },
        "aggs": {
            "region_agg": {
                "terms": {
                    "field": "region.raw",
                    "size":   1000000,
                },
                "aggs": {
                    "metric_agg": {
                        "terms": {
                            "field": "metric.raw",
                            "size":   1000000,
                        },
                        "aggs": {
                            "per_period": {
                                "date_histogram": {
                                    "field": "timestamp",
                                    "interval": interval_map[period],
                                    "format": "yyyy-MM-dd'T'H:m:s+00:00",
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
                        }
                    }
                }
            }
        }
    }

    r = requests.post(es_url + "/_search?&pretty", json=request_body)

    buckets = r.json()['aggregations']['region_agg']['buckets']

    region_list = []

    for bucket in buckets:
        print(bucket['key'])
        metric_list = []
        for metric_bucket in bucket['metric_agg']['buckets']:
            data_points = []
            for per_period_bucket in metric_bucket['per_period']['buckets']:
                data_point = {
                    'timestamp': per_period_bucket['key_as_string'],
                    'unixtimestamp': per_period_bucket['key'],
                    'avg': per_period_bucket['extended_stats_agg']['avg'],
                    'min': per_period_bucket['extended_stats_agg']['min'],
                    'max': per_period_bucket['extended_stats_agg']['max'],
                    'percentile_1_0': per_period_bucket['percentiles_agg']['values']['1.0'],
                    'percentile_5_0': per_period_bucket['percentiles_agg']['values']['5.0'],
                    'percentile_25_0': per_period_bucket['percentiles_agg']['values']['25.0'],
                    'percentile_50_0': per_period_bucket['percentiles_agg']['values']['50.0'],
                    'percentile_75_0': per_period_bucket['percentiles_agg']['values']['75.0'],
                    'percentile_95_0': per_period_bucket['percentiles_agg']['values']['95.0'],
                    'percentile_99_0': per_period_bucket['percentiles_agg']['values']['99.0']
                }
                data_points.append(data_point)
            metric_list.append({metric_bucket['key']: data_points})
        region_list.append({bucket['key']: metric_list})

    return flask.jsonify([region_list])


@app.route("/api/v1/region/<region>/<period>")
def get_perf_for_region(region,  period):
    request_body = {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "timestamp": {
                                "gte": period_map[period],
                                "lt":  "now",
                                "format": "yyyy-MM-dd'T'H:m:s+00:00"
                            }
                        }
                    },
                    {
                        "match": {"region": region}
                    }
                ]
            }
        },
        "aggs": {
            "metric_agg": {
                "terms": {
                    "field": "metric.raw",
                    "size":   1000000,
                },
                "aggs": {
                    "per_period": {
                        "date_histogram": {
                            "field": "timestamp",
                            "interval": interval_map[period],
                            "format": "yyyy-MM-dd'T'H:m:s+00:00",
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
                }
            }
        }
    }

    r = requests.post(es_url + "/_search?&pretty", json=request_body)
#    agg = r.json()['aggregations']['metric_agg']['buckets'][0]
    buckets = r.json()['aggregations']['metric_agg']['buckets']

    metric_list = []

    for bucket in buckets:
        data_points = []
        for per_period_bucket in bucket['per_period']['buckets']:
            data_point = {
                'timestamp': per_period_bucket['key_as_string'],
                'unixtimestamp': per_period_bucket['key'],
                'avg': per_period_bucket['extended_stats_agg']['avg'],
                'min': per_period_bucket['extended_stats_agg']['min'],
                'max': per_period_bucket['extended_stats_agg']['max'],
                'percentile_1_0': per_period_bucket['percentiles_agg']['values']['1.0'],
                'percentile_5_0': per_period_bucket['percentiles_agg']['values']['5.0'],
                'percentile_25_0': per_period_bucket['percentiles_agg']['values']['25.0'],
                'percentile_50_0': per_period_bucket['percentiles_agg']['values']['50.0'],
                'percentile_75_0': per_period_bucket['percentiles_agg']['values']['75.0'],
                'percentile_95_0': per_period_bucket['percentiles_agg']['values']['95.0'],
                'percentile_99_0': per_period_bucket['percentiles_agg']['values']['99.0']
            }
            print(pretty_js(data_point))
            data_points.append(data_point)
        metric_list.append({bucket['key']: data_points})

    return flask.jsonify([metric_list])


if __name__ == "__main__":
    main()
