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

import json
import os

import requests
import six

import datetime


from rally import api
from rally.common import logging
from rally import exceptions
from rally.task import exporter

LOG = logging.getLogger(__name__)


@exporter.configure(name="es")
class ESExporter(exporter.Exporter):

    def validate(self):
        """Validate connection string.

        The format of connection string in ElasticSearch plugin is
            es:///<path>?region=<region>
        """
        LOG.debug("Region: %s " % self.region)
        LOG.debug("URI: %s " % self.url)

        parse_obj = six.moves.urllib.parse.urlparse(self.connection_string)

        if self.connection_string is None or parse_obj.path == "":
            raise exceptions.InvalidConnectionString(
                "It should be `es:///<ip_or_hostname>?region=<region>`.")
        if not self.region:
            raise exceptions.InvalidConnectionString(
                "Invalid or undefined region")

    def __init__(self, connection_string):
        super(ESExporter, self).__init__(connection_string)
        parse_obj = urlparse.urlparse(self.connection_string)
        self.region = (urlparse.parse_qs(parse_obj.query)['region'][0])
        self.url = parse_obj.path.split('/')[-1]
        self.proto = 'http://'
        self.validate()

    def export(self, uuid):
        """Export results of the task to the file.

        :param uuid: uuid of the task object
        """

        task = api.Task.get(uuid)

        LOG.debug("Got the task object by it's uuid %s. " % uuid)

        task_results = [{"key": x["key"], "result": x["data"]["raw"],
                         "sla": x["data"]["sla"],
                         "hooks": x["data"].get("hooks"),
                         "load_duration": x["data"]["load_duration"],
                         "full_duration": x["data"]["full_duration"]}
                        for x in task.get_results()]

        es_data_list = []
        if task_results:
            LOG.debug("Got the task %s results." % uuid)
            for task_result in task_results:
                for result in task_result['result']:
                    if not result['error']:
                        atomic_actions = result['atomic_actions']
                        for k, v in six.iteritems(atomic_actions):
                            es_data = {
                                'region': self.region,
                                'metric': k,
                                'value': v,
                                'timestamp': (
                                    datetime.datetime.now().isoformat()
                                )
                            }
                            es_data_list.append({'index': {}})
                            es_data_list.append(es_data)
        else:
            msg = ("Task %s results would be available when it will "
                   "finish." % uuid)
            raise exceptions.RallyException(msg)

        es_request_data = '\n'.join([json.dumps(x) for x in es_data_list])

        LOG.debug("ES Data: \n %s ", es_request_data)

        es_url = self.proto + self.url + '/performance/key_metrics/_bulk'
        try:
            r = requests.post(es_url, data=es_request_data)
            LOG.debug("Status code: %s", r.status_code)
            LOG.debug("Response: %s", r.json())
        except Exception as e:
            raise exceptions.RallyException(e)
