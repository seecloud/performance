#!/bin/bash

#set -x

RALLY='/usr/local/bin/rally'
TASK_FILE='/opt/perf/cron_jobs/task.yaml'
RALLY_DEPLOYMENT_NAME='rally'

if [ "x${RALLY_CONNECTION_STRING}" == "x" ]
then
  # do nothing if connection string is not defined
  echo "RALLY_CONNECTION_STRING is not defined"
  exit 0
fi

${RALLY} deployment list

# Create deployment if it does not exist
${RALLY} deployment list | grep "${RALLY_DEPLOYMENT_NAME}" || (
  echo "Creating deployment:   rally deployment create --fromenv --name=${RALLY_DEPLOYMENT_NAME}"
  env

  if [ "x${OS_PROJECT_NAME}" == "x" ]
  then
    if [ "x${OS_TENANT_NAME}" == "x"  ]
    then
      echo "OS_PROJECT_NAME or  OS_TENANT_NAME is not defined"
      exit 0
    fi
  fi

  if [ "x${OS_USERNAME}" == "x" ]
  then

    echo "OS_USERNAME is not defined"
    exit 0

  fi

  if [ "x${OS_PASSWORD}" == "x" ]
  then

    echo "OS_PASSWORD is not defined"
    exit 0

  fi

  if [ "x${OS_AUTH_URL}" == "x" ]
  then

    echo  "OS_AUTH_URL is  not defined"
    exit 0

  fi

  ${RALLY} deployment create --fromenv --name=rally && ${RALLY} deployment  use ${RALLY_DEPLOYMENT_NAME}
)

# run task
${RALLY} deployment  use ${RALLY_DEPLOYMENT_NAME}

TASK_UUID=`${RALLY} \
task start  ${TASK_FILE} | tee /dev/stderr \
| grep 'rally task results '\
| awk '{ print $4 }' \
| sort \
| uniq`;

echo UUID=${TASK_UUID}

${RALLY} --plugin-paths=/opt/perf/rally_plugins  \
task export \
--uuid ${TASK_UUID} \
--connection ${RALLY_CONNECTION_STRING}

