FROM ubuntu:16.04
MAINTAINER Sergey Skripnick <sskripnick@mirantis.com>

# install prereqs
RUN apt-get update && apt-get install --yes wget python vim bash-completion gcc cron git supervisor sudo  && \
  wget https://bootstrap.pypa.io/get-pip.py && \
  python get-pip.py && \
  rm -f get-pip.py && \
  useradd -u 65500 -m rally && \
  usermod -aG sudo rally && \
  echo "rally ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/00-rally-user && \
  ln -s /opt/rally/doc /home/rally/rally-docs

# install rally. the COPY command below frequently invalidates
# subsequent cache
COPY . /tmp/rally
WORKDIR /tmp/rally
RUN ./install_rally.sh --system --verbose --yes \
    --db-name /home/rally/.rally.sqlite && \
  pip install -r optional-requirements.txt && \
  mkdir /opt/rally/ && \
  # TODO(andreykurilin): build docs to rst before move, since we have several
  # extensions.
  mv certification/ samples/ doc/ /opt/rally/ && \
  chown -R rally /opt/rally /etc/rally && \
  rm -rf /tmp/* && \
  mkdir -p /opt/perf/src && \
  mkdir -p /opt/perf/rally_plugins && \ 
  mkdir -p /opt/perf/cron_jobs && \
  cd  /opt/perf/src && ls -lsa && pwd && \
  git clone https://github.com/sirmax123/performance.git && \
  ls -lsa && pwd && \
  cp performance/performance/collector/es.py  /opt/perf/rally_plugins && \ 
  cp performance/performance/collector/cron_job.sh  /opt/perf/cron_jobs && \
  cp performance/performance/collector/task.yaml  /opt/perf/cron_jobs && \
  mkfifo --mode 0666 /var/log/cron.log && \
  echo '#!/usr/bin/env bash \n\ 
set -e \n\
\n\
env | while read -r LINE; do \n\
    IFS="=" read VAR VAL <<< ${LINE} \n\
    sed --in-place "/^${VAR}/d" /etc/security/pam_env.conf || true \n\
    echo "${VAR} DEFAULT=\"${VAL}\"" >> /etc/security/pam_env.conf \n\
done \n\
\n\
exec "$@" \n\
' > /docker-entrypoint.sh && \
  chmod +x /docker-entrypoint.sh && \
  echo '* * * * * root flock -n -E 0  /opt/perf/cron_jobs/cron_job.sh -c  /opt/perf/cron_jobs/cron_job.sh >> /var/log/cron.log 2>&1'  >> /etc/cron.d/rally && \
  echo  '[supervisord] \n\
nodaemon=true \n\
stdout_logfile=/dev/fd/1 \n\
stdout_logfile_maxbytes=0 \n\
\n\
[program:bash] \n\
command=/bin/bash --login \n\
stdout_logfile=/dev/fd/1 \n\
stdout_logfile_maxbytes=0 \n\
\n\
[program:cron]  \n\
command=cron -f \n\
stdout_logfile=/dev/fd/1 \n\
stdout_logfile_maxbytes=0 \n\
\n\
[program:cronlogs]  \n\
command=tail -f /var/log/cron.log \n\
stdout_logfile=/dev/fd/1 \n\
stdout_logfile_maxbytes=0 ' >/etc/supervisor/conf.d/supervisord.conf



VOLUME ["/home/rally"]

WORKDIR /home/rally/

USER root
ENV HOME /home/rally/


RUN rally-manage db recreate

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["/usr/bin/supervisord"]

