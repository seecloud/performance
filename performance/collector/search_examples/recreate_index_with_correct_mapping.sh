#!/bin/bash



source ./settings

${CURL} -XGET "${ES_URL}/${INDEX_NAME}/${TYPE_NAME}/_mapping?pretty" 

exit
#
#${CURL} -XGET "${ES_URL}/${INDEX_NAME}/_mapping?pretty" 
#
#
#exit
#${CURL} -XPUT "${ES_URL}/${INDEX_NAME}/_mapping/${TYPE_NAME}" -d " 
#{
#        \"properties\" : {
#          \"metric\" : {
#            \"type\" : \"text\",
#            \"fielddata\": true,
#            \"index\":    \"not_analyzed\"
#            }
#          }
#       
#}
#"
#exit

${CURL} -XDELETE "${ES_URL}/${INDEX_NAME}"
echo "======="
${CURL} -XPUT    "${ES_URL}/${INDEX_NAME}" -d " 
{
    \"mappings\" : {
      \"key_metrics\" : {
        \"properties\" : {
          \"metric\" : {
            \"fielddata\" : true,
            \"type\" : \"string\",
            \"fields\" : {
              \"raw\" : {
                \"type\": \"string\",
                \"index\": \"not_analyzed\"
                }
              }
          },
          \"region\" : {
            \"type\" : \"string\",
            \"fielddata\": true,
            \"fields\" : {
              \"raw\" : {
                \"type\": \"string\",
                \"index\": \"not_analyzed\"
              }
            }
          }, 
          \"timestamp\" : {
            \"type\" : \"date\"
          },
          \"value\" : {
            \"type\" : \"float\"
          }
        }
      }
    }
}
"
