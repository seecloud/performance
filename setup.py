#!/usr/bin/env python

from distutils.core import setup

setup(name="performance",
      version="0.1",
      description="Collect cloud key performance metrics",
      url="https://github.com/seecloud/performance",
      author="<name>",
      author_email="<name>@mirantis.com",
      packages=["performance"],
      package_dir={"performance": "performance"},
      package_data={"performance": ["tasks/*.json", "tasks/*.yaml"]})
