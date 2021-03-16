from string import Template
import time
from .common import *

def dataset_pid(protocol, authority, identifier):
    return '{}:{}/{}'.format(protocol, authority, identifier)

class Dataverse(object):
    _attr_required_metadata = ['alias', 'name', 'dataverseContacts']
    _attr_valid_metadata = _attr_required_metadata + \
                           ['affiliation', 'description', 'dataverseType']
    _attr_valid_class = ['pid'] + _attr_valid_metadata

    def __init__(self, connection, data):
        self.connection = connection
        self.datasets = []
        self.dataverses = []
        self.identifier = data['id']
        self.pid = None
        self.name = data['name']
        self.alias = data['alias']
        self.dataverseContacts = data.get('dataverseContacts', [])
        self.affiliation = None
        self.description = data.get('description', '')
        self.dataverseType = data['dataverseType']
        self.ctime = data.get('creationDate', None)

    def __str__(self):
        return 'Dataverse {} name={} alias={}'.format(self.identifier, self.name, self.alias)

    def find_dataverse(self, name, auth=True):
        result = [child for child in self.contents() if child.name == name]
        if result:
            return result[0]
        else:
            raise DataverseError("Dataverse {0} does not have child dataverse '{}'".\
                                 format(self.identifier, name))

    def create_dataverse(self, metadata, auth=True):
        """Create a new dataverse within the present dataverse.
        To create a dataverse, you must create a dict variable `metadata`
        containing the minimal metadata.
        Example:
        metadata = {'name': 'Rats', 'alias': 'rats',
                    'dataverseContacts': [{'contactEmail':'dm_rats@umcutrecht.nl'}]}
        """
        endpoint = '/dataverses/{0}'.format(self.alias)
        metadata['dataverseType'] = 'RESEARCH_GROUP'
        valid = all(bool(metadata.get(attr, None)) for attr in self._attr_required_metadata)
        if not valid:
            raise DataverseError('Invalid metadata for new child of dataverse {0}'.\
                                 format(self.identifier))
        response = self.connection.post_request(endpoint, metadata=metadata, auth=auth)
        code = response.status_code
        message = response.json().get('message', '')
        if code in (200, 201):
            return Dataverse(connection=self.connection, data=response.json()['data'])
        elif code == 404:
            raise DataverseError('Dataverse {0} was not found: {1} (404)'.\
                                 format(self.alias, message))
        else:
            raise DataverseError('Child of dataverse {0} could not be created: {1} ({2})'.\
                                 format(self.identifier, message, code))

    def create_dataset(self, metadata, auth=True, test=False):
        """Add new dataset to this dataverse.
        To create a dataset, you must create a JSON file containing all the
        metadata in `dataset-minimal-metadata.json`. The contents of this file
        are a template string with replacement fields: $title $authorname
        $authoraffiliation $contactemail $contactname $description.
        The replacements should be in the dict variable `metadata`."""
        endpoint = '/dataverses/{0}/datasets'.format(self.identifier)
        template = read_file('dataset-minimal-metadata.json')
        result = Template(template).substitute(metadata)
        if test:
            print('add dataset with metadata {}'.format(result))
        response = self.connection.post_request(endpoint, metadata=result, auth=auth)
        code = response.status_code
        message = response.json().get('message', '')
        if code == 201:
            return Dataset(connection=self.connection, data=response.json()['data'])
        elif code == 404:
            raise DataverseError('Dataverse {0} was not found: {1} (404)'.\
                                 format(self.alias, message))
        else:
            raise DataverseError('Dataset could not be created: {0} ({1})'.\
                                 format(message, code))

    def publish(self, auth=True):
        endpoint = '/dataverses/{0}/actions/:publish'.format(self.identifier)
        response = self.connection.post_request(endpoint, auth=auth)
        code = response.status_code
        message = response.json().get('message', '')
        if code == 200:
            return True
        elif code == 401:
            raise DataverseError('No authorization to publish dataverse {0}: {1} (401)'.\
                                 format(self.identifier, message))
        elif code == 404:
            raise DataverseError('Dataverse {0} was not found: {1} (404)'.\
                                 format(self.identifier, message))
        else:
            raise DataverseError('Dataverse {0} could not be published: {1} ({2})'.\
                                 format(self.identifier, message, code))

    def contents(self, json=False):
        endpoint = '/dataverses/{0}/contents'.format(self.identifier)
        response = self.connection.get_request(endpoint, auth=True)
        if json:
            return response.json()['data']
        else:
            result = []
            for el in response.json()['data']:
                if el['type'] == 'dataverse':
                    lookup_id = el['id']
                    result.append(self.connection.get_dataverse(lookup_id, auth=True))
                elif el['type'] == 'dataset':
                    # persistentId = doi:10.5072/FK2/J8SJZB
                    lookup_id = dataset_pid(el['protocol'], el['authority'], el['identifier'])
                    result.append(self.connection.get_dataset(lookup_id, is_pid=True, auth=True))
            return result

    def delete(self, auth=True):
        endpoint = '/dataverses/{0}'.format(self.identifier)
        response = self.connection.delete_request(endpoint, auth)
        code = response.status_code
        message = response.json().get('message', '')
        if code == 200:
            self.connection = None  # object remains alive, but is useless without connection
            return True
        elif code == 401:
            raise DataverseError('No authorization to delete dataverse {0}: {1} (401)'.\
                                 format(self.identifier, message))
        elif code == 404:
            raise DataverseError('Dataverse {0} was not found: {1} (404)'.\
                                 format(self.identifier, message))
        elif code == 403:
            raise DataverseError('Dataverse {0} not empty: {1} (403)'.\
                                 format(self.identifier, message))
        else:
            raise DataverseError('Dataverse {0} could not be deleted: {1} ({2})'.\
                                 format(self.identifier, message, code))


class Dataset(object):
    _attr_required_metadata = ['title', 'author', 'datasetContact', 'dsDescription', 'subject']

    def __init__(self, connection, data):
        print("Dataset.init: data={}".format(data))
        self.connection = connection
        self.dataset_id = data.get('id', '')
        self.identifier = data.get('identifier', '')
        self.protocol = data.get('protocol', '')
        self.authority = data.get('authority', '')
        self.datafiles = []
        self.ctime = data['latestVersion']['createTime'] if 'latestVersion' in data else None
        self.title = None
        self.author = []
        self.datasetContact = []
        self.dsDescription = []
        self.subject = []

    def pid(self):
        return dataset_pid(self.protocol, self.authority, self.identifier)

    def __str__(self):
        return 'Dataset {} persistentId={} ctime={}'.\
               format(self.dataset_id, self.pid(),self.ctime)

    def publish(self, dstype='minor', auth=True):
        endpoint = '/datasets/:persistentId/actions/:publish?persistentId={0}&type={1}'.\
                 format(self.pid(), dstype)
        response = self.connection.post_request(endpoint, auth=auth)
        code = response.status_code
        message = response.json().get('message', '')
        if code == 200:
            return True
        elif code == 404:
            raise DataverseError('Dataset {0} was not found: {1} (404)'.\
                                 format(self.identifier, message))
        elif code == 401:
            raise DataverseError('No authorization to publish dataset {0}: {1} (401)'.\
                                 format(self.identifier, message))
        else:
            raise DataverseError('Dataset {0} could not be published: {1} ({2})'.\
                                 format(self.identifier, message, code))

    def delete(self, is_pid=True, auth=True):
        if is_pid:
            endpoint = '/datasets/:persistentId/?persistentId={0}'.format(self.pid())
        else:
            endpoint = '/datasets/{0}'.format(self.dataset_id)
        response = self.connection.delete_request(endpoint, auth=auth)
        code = response.status_code
        message = response.json().get('message', '')
        if code == 200:
            self.connection = None  # object remains alive, but is useless without connection
            return True
        elif code == 404:
            raise DataverseError('Dataset {0} was not found: {1} (404)'.\
                                 format(self.identifier, message))
        elif code == 405:
            raise DataverseError('Published datasets can only be deleted from the GUI: {} (405)'.\
                                 format(message))
        elif code == 401:
            raise DataverseError('No authorization to publish dataset {0}: {1} (401)'.\
                                 format(self.identifier, message))
        else:
            raise DataverseError('Dataset {0} could not be deleted: {1} ({2})'. \
                                 format(self.identifier, message, code))

    def versions(self):
        endpoint = '/datasets/{0}/versions'.format(self.dataset_id)
        response = self.connection.get_request(endpoint, auth=True)
        return response.json()

    def get_datafiles(self, version='1'):
        endpoint = '/datasets/:persistentId/versions/{0}/files?persistentId={1}'.\
                 format(version, self.pid())
        response = self.connection.get_request(endpoint, auth=True)
        return response.json()

    def get_datafile(self, identifier, is_pid=True):
        if is_pid:
            endpoint = '/access/datafile/{0}'.format(identifier)
        else:
            endpoint = '/access/datafile/:persistentId/?persistentId={0}'.format(identifier)
        response = self.connection.get_request(endpoint, auth=True)
        return response.json()

    def add_file(self, filename, metadata, test=False):
        """Add file to the present dataset. The argument `metadata` should
        be a dict object containing at least description (str),
        directoryLabel (str, relative file path), restrict = True|False
        Via the shell, one would add a file like so:
        /usr/bin/curl -H X-Dataverse-key:2a4e470d-c316-48c3-9a30-1d819b0bdbc8 \
         -X POST -F 'file=@description.json' \
         -F 'jsonData={"description": "description of file 1",
                       "directoryLabel": "foo/bar",
                       "restrict": false, "categories": ["Data"]}' \
         http://localhost:8080/api/datasets/61/add
        """
        if 'categories' not in metadata:
            metadata['categories'] = ['Data']
        json_data = json.dumps(metadata)
        params = {'file':open(filename, 'rb'), 'jsonData':json_data}
        if test:
            print('add file {} with metadata {}'.format(filename, json_data))
        endpoint = '/datasets/{0}/add'.format(self.dataset_id)
        response = self.connection.post_request(endpoint, files=params, auth=True)
        code = response.status_code
        resp_json = response.json()
        message = resp_json.get('message', '')
        if code == 200:
            # Dataverse server needs some time in between file uploads.
            # If you omit this, you run the risk of HTTP 400 on some of the requests.
            time.sleep(1)
            return True
        elif code == 404:
            raise DataverseError('Dataset {0} was not found: {1} (404)'.\
                                 format(self.dataset_id, message))
        elif code == 400:
            raise DataverseError('Bad request adding file to dataset {0}: {1} (400)'.\
                                 format(self.identifier, resp_json))
        elif code == 401:
            raise DataverseError('No authorization to add file to dataset {0}: {1} (401)'. \
                                 format(self.identifier, message))
        else:
            raise DataverseError('Dataset {0}: file could not be added: {1} ({2})'. \
                                 format(self.identifier, message, code))

"""Response of add_file should look like this:
{
  "status": "OK",
  "data": {
    "files": [
      {"description":"description of file 1",
      "label":"description.json",
      "restricted":false, "directoryLabel":"foo/bar",
      "version":1, "datasetVersionId":4,
      "categories":["Data"],
      "dataFile":{
        "id":63, "persistentId":"", "pidURL":"",
        "filename":"description.json", "contentType":"application/json",
        "filesize":244,
        "description":"description of file 1",
        "storageIdentifier":"171d0350487-867543c06935",
        "rootDataFileId":-1,
        "md5":"73ddb07268f0e151a3236c79a4a1b6ac",
        "checksum":{"type":"MD5","value":"73ddb07268f0e151a3236c79a4a1b6ac"},
  "creationDate":"2020-05-01"}}]
  }
}
"""

class Datafile(object):
    _attr_required_metadata = ['filename', 'pid']
    _attr_valid_metadata = ['description', 'pid','restrict']
    _attr_valid_class = ['filename'] + _attr_valid_metadata

    def __init__(self, filename=None, pid=None):
        self.pid = pid
        self.filename = filename
        self.description = None
        self.restrict = None
