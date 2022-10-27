#!/usr/bin/env sh

/usr/bin/curl -H X-Dataverse-key:xxxxxxxx-yyyy-zzzz-wwww-vvvvvvvvvvvv \
 -X POST -F 'file=@description.json' \
 -F 'jsonData={"description": "description of file 1", "directoryLabel": "foo/bar", "restrict": false, "categories": ["Data"]}' \
 http://localhost:8080/api/datasets/61/add
