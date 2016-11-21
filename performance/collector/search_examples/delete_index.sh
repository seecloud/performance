#!/bin/bash


source ./settings

${CURL} -XDELETE "http://172.18.196.234:9200/${INDEX_NAME}"

