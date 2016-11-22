#!/bin/bash


source ./settings

${CURL} -XGET "${ES_URL}/${INDEX_NAME}/${TYPE_NAME}/_search?pretty" -d"
{
     \"size\": 10000, 
        \"query\": {
        \"bool\": { 
        \"must\": [
        {
            \"range\" : {
                \"timestamp\" : {
                    \"gte\" : \"now-1d\",
                    \"lt\" :  \"now\",
                    \"format\" : \"yyyy-MM-dd'T'H:m:s+00:00\"
                }
            }
        },
        { \"match\": { \"region\": \"myRegion3\" }}
        ]
        }
      },
      \"aggs\" : {
            \"metric_agg\" : {
                \"terms\" : { 
        	    \"field\" : \"metric.raw\",
        	    \"size\" : 1000000
                }
            }
       }
}
"
exit
        { \"match\": { \"metric\": \"nova.create_keypair\" }}
