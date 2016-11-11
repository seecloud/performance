Performance Service Configuration
=================================

Placement
---------

Configuration file should be placed to */etc/oss/performance/config.json*.

If there is an environment variable *PERFORMANCE_CONF* set, it is used as priority.
In this case it is important to use absolute path to configuration file.

Example:

.. code-block::

    export PERFORMANCE_CONF=/home/username/oss_configs/performance.json
    python performance.main

Configuration File Description
------------------------------

Configuration file is plain JSON document with top level keys which define
`Flask <http://flask.pocoo.org>`_ and `Rally <https://github.com/openstack/rally>`_
configuration:

Here is a simple example:

.. code-block::

  {
      "flask": {
          "PORT": 5010,
          "HOST": "0.0.0.0",
          "DEBUG": false
      },
      "rally": {
          "tasks": {
              "boot_servers": {
                  "input_file": "path/to/tasks/boot_servers.json",
                  "tag": "servers",
                  "template_args": {"image": "ubuntu16.04-server"},
                  "plugin_paths": null
              }
          },
          "plugin_paths": null,
          "log_dir": null,
          "log_file": null,
          "log_verbose": false
      }
  }

Flask configuration
~~~~~~~~~~~~~~~~~~~

Flask configuration is set via *flask* key and described in
`official documentation <http://flask.pocoo.org/docs/0.11/config/>`_.

The only extra options are *HOST* and *PORT*.

Rally configuration
~~~~~~~~~~~~~~~~~~~

This configures `Rally <https://github.com/openstack/rally>`_.

Parameters explanation:

* *rally/tasks* - object that describes tasks available to run by the service.
  Key is task name and value is task configuration
* *rally/tasks/<name>/input_file* - path to task input file.
  Input file could be in JSON or YAML format
* *rally/tasks/<name>/tag* - related tag name or null
* *rally/tasks/<name>/template_args* - null or object with data
  for input file transformation by template processor (Jinja2)
* *rally/tasks/<name>/plugin_paths* - null or array of paths where
  Rally can find plugins required for this specific task
* *rally/plugin_paths* - null or array of paths that are loaded
  for each task
* *rally/log_file* - path to log file
* *rally/log_dir* - null or path to base directory used for relative
                  log_file paths
* *rally/log_verbose* - boolean, 'true' increases logging level to WARNING
