FROM ubuntu:16.04
MAINTAINER Max Mazur <mmaxur@mirantis.com>


USER root

RUN \
  apt-get update && \
  apt-get install --yes wget python vim bash-completion gcc  git python-pip python-requests

RUN \
  mkdir -p /opt/perf/src && \
  mkdir -p /etc/oss/performance/api && \
  mkdir -p /opt/perf/api && \
  pip install -U flask

RUN \
  cd /opt/perf/src && \
  git clone https://github.com/seecloud/performance.git && \
  cp performance/performance/main.py  /opt/perf/api

EXPOSE 5010

CMD ["/usr/bin/python", "/opt/perf/api/main.py"]
