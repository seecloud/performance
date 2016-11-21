#!/bin/bash


source ./settings


#${CURL} -XGET "${ES_URL}/${INDEX_NAME}/${TYPE_NAME}/_search?pretty" -d'
#{
#  "size": 10000,
#  "sort": [{"timestamp": "desc"}]
#}'


${CURL} -XGET "${ES_URL}/${INDEX_NAME}/${TYPE_NAME}/_search?pretty" -d"
{
     \"size\": 0, 
        \"query\": {
        \"bool\": { 
        \"must\": [
        {
            \"range\" : {
                \"timestamp\" : {
                    \"gte\" : \"now-1d/d\",
                    \"lt\" :  \"now\",
                    \"format\" : \"yyyy-MM-dd'T'H:m:s+00:00\"
                }
            }
        },
        { \"match\": { \"region\": \"myRegion3\" }},
        { \"match\": { \"metric\": \"nova.boot_server\" }}
        ]
        }
      },
      \"aggs\" : {
            \"per_period\" : {
                \"date_histogram\" : {
                    \"field\" : \"timestamp\",
                    \"interval\" : \"1H\",
                    \"format\" : \"yyyy-MM-dd'T'H:m:s+00:00\"
                },
                \"aggs\": {
                    \"extended_stats_agg\": {
                        \"extended_stats\": {
                            \"field\": \"value\"
                        }
            	    },
                    \"percentiles_agg\": {
                        \"percentiles\": {
                            \"field\": \"value\"
                        }
                    }            	                	    
                }
            }
    	}            
}"
