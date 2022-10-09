#!/usr/bin/env bash
# production
# export SERVER_URL=https://dataverse.nl
# export API_TOKEN=7cfc5b8f-3c8d-4c50-8bd5-2a56ad1ef51b
# demo
export SERVER_URL=https://demo.dataverse.nl
export API_TOKEN=5bf24ffd-1789-480f-b8a2-4ee18a9b895a
curl -H "X-Dataverse-key:$API_TOKEN" $SERVER_URL/api/dataverses/45/contents > dvview.json
