#!/bin/bash


DOCKER='/usr/bin/docker'
DOCKER_CONTAINER='95ea5b320918'

TASK_LOG="/var/log/task.log"
TASK_FILE="/home/rally/task.yaml"

CONNECTION_STRING='es:///172.18.196.234:9200.myRegion1'


TASK_UUID=`${DOCKER} exec ${DOCKER_CONTAINER} \
rally task start 2>&1 ${TASK_FILE} \
| tee -a ${TASK_LOG} \
| grep 'rally task results '\
| awk '{ print $4 }' \
| sort \
| uniq`; 


${DOCKER} exec ${DOCKER_CONTAINER} \
rally --plugin-paths=/home/rally/plugins  \
task export \
--uuid ${TASK_UUID} \
--connection ${CONNECTION_STRING} 2>&1 >> ${TASK_LOG}
