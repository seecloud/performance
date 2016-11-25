FROM rallyforge/rally:latest
MAINTAINER Max Mazur <mmaxur@mirantis.com>


USER root

RUN \
  apt-get update && \
  apt-get install --yes wget python vim bash-completion gcc cron git supervisor

RUN \
  mkdir -p /opt/perf/src && \
  mkdir -p /opt/perf/rally_plugins && \
  mkdir -p /opt/perf/cron_jobs && \
  mkdir -p /etc/oss/performance

RUN \
  cd /opt/perf/src && \
  git https://github.com/seecloud/performance.git && \
  cp performance/performance/collector/es.py  /opt/perf/rally_plugins && \
  cp performance/performance/collector/cron_job.sh  /opt/perf/cron_jobs && \
  cp performance/performance/collector/task.yaml  /opt/perf/cron_jobs && \
  mkfifo --mode 0666 /var/log/cron.log

RUN \
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
' > /docker-entrypoint.sh

RUN \
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
