#!/usr/bin/env bash
# production
# export SERVER_URL=https://dataverse.nl
# export API_TOKEN=zzzzzzz-yyyy-xxxx-wwww-vvvvvvvvvvvv
# demo
export SERVER_URL=https://demo.dataverse.nl
export API_TOKEN=zzzzzzz-yyyy-xxxx-wwww-vvvvvvvvvvvv
curl -H "X-Dataverse-key:$API_TOKEN" $SERVER_URL/api/dataverses/45/contents > dvview.json
