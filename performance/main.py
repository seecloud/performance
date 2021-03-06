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
from flask_helpers import routing

from performance import api
from performance import config

app = flask.Flask(__name__, static_folder=None)
app.config.update(config.get_config()["flask"])


for module in [api]:
    for url_prefix, blueprint in module.get_blueprints():
        app.register_blueprint(blueprint, url_prefix="/api%s" % url_prefix)


app = routing.add_routing_map(app, html_uri=None, json_uri="/")


@app.errorhandler(404)
def not_found(error):
    return flask.jsonify({"error": "Not Found"}), 404


def main():
    app.run(host=app.config.get("HOST", "0.0.0.0"),
            port=app.config.get("PORT", 5010))


if __name__ == "__main__":
    main()
