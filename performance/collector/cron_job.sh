#!/bin/bash



#RALLY_CONNECTION_STRING='es:///172.18.196.234:9200.myRegion1'

if [ "x${RALLY_CONNECTION_STRING}" == "x" ]
then
  # do nothing if connection string is not defined
  echo "RALLY_CONNECTION_STRING is not defined"
  exit 0
fi

# Create deployment if it does not exist
rally deployment list | grep '*' || (
  echo "Creating deployment:   rally deployment create --fromenv --name=rally"
  env
  rally deployment create --fromenv --name=rally
)

# run task

TASK_UUID=`rally task start 2>&1 ${TASK_FILE} \
| tee -a ${TASK_LOG} \
| grep 'rally task results '\
| awk '{ print $4 }' \
| sort \
| uniq`; 


rally --plugin-paths=/opt/perf/rally_plugins  \
task export \
--uuid ${TASK_UUID} \
--connection ${RALLY_CONNECTION_STRING}

