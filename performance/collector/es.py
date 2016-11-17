
import json
import requests
import six
import os



from six.moves.urllib import parse as urlparse
from datetime import datetime


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
            es:///<path>.<region>
        """
        print(self.region)
        print(self.url)

        parse_obj = urlparse.urlparse(self.connection_string)
        print(parse_obj)

        if self.connection_string is None or parse_obj.path == "":
            raise exceptions.InvalidConnectionString(
                "It should be `es:///<ip_or_hostname>.<region>`.")
        if not self.region:
            raise exceptions.InvalidConnectionString(
                "Invalid or undefined region")

    def __init__(self, connection_string):
        super(ESExporter, self).__init__(connection_string)
        self.path = os.path.expanduser(urlparse.urlparse(
            connection_string).path[1:])
        self.region = connection_string.split(".")[-1]
        self.url = connection_string.replace('.' + self.region,'').split('/')[-1]
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

        es_data_list = ""
        if task_results:
            LOG.debug("Got the task %s results." % uuid)
            for task_result in task_results:
                for result in task_result['result']:
                    if not result['error']:
                        atomic_actions = result['atomic_actions']
                        for k, v  in  six.iteritems(atomic_actions):
                            es_data = {'region': self.region, 'metric': k, 'value': v,  'timestamp': str(datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")) }
                            es_data_list =  es_data_list + str(json.dumps({'index': {}})) + "\n" + str(json.dumps(es_data)) + "\n"
        else:
            msg = ("Task %s results would be available when it will "
                  "finish." % uuid)
            raise exceptions.RallyException(msg)

        print(json.dumps(es_data, sort_keys=True, indent=4))
        es_url = self.proto + self.url + '/performance/key_metrics/_bulk'
        try:
            r = requests.post(es_url, data = str(es_data_list))
        except Exception as e:
            raise exceptions.RallyException(e)
