#!/usr/bin/env sh

/usr/bin/curl -H X-Dataverse-key:2a4e470d-c316-48c3-9a30-1d819b0bdbc8 \
 -X POST -F 'file=@description.json' \
 -F 'jsonData={"description": "description of file 1", "directoryLabel": "foo/bar", "restrict": false, "categories": ["Data"]}' \
 http://localhost:8080/api/datasets/61/add