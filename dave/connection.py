from datetime import datetime
import json, sys
from requests import ConnectionError, delete, get, put, post
from .common import DataverseError
from .models import Dataverse, Dataset

method_callable = {
    'GET': get, 'PUT': put, 'POST': post, 'DELETE': delete
}

class Connection:
    def __init__(self, base_url, api_token=None, api_version='v1'):
        if not isinstance(base_url, str):
            raise ConnectionError('base_url {0} is not a string'.format(base_url))
        self.base_url = base_url
        if not isinstance(api_version, str):
            raise ConnectionError('api_version {0} is not a string'.format(api_version))
        self.api_version = api_version
        if api_token:
            if not isinstance(api_token, str):
                raise ConnectionError('api_token is not a string')
        self.api_token = api_token
        self.connection_started = datetime.now()
        query = '/info/server'
        if base_url and api_version:
            self.native_api_base_url = '{0}/api'.format(self.base_url)
            url = '{0}{1}'.format(self.native_api_base_url, query)
            try:
                response = get(url)
                if response:
                    self.status = response.json()['status']
                    print('Succesfully created connection with request {0}'.format(url))
                else:
                    self.status = 'error'
                    raise ConnectionError('Received no response on request {0}'.format(url))
            except Exception as e:
                self.status = 'error'
                raise ConnectionError('Could not create connection to {0} ({1})'.format(url, e))
        else:
            self.status = 'error'
            self.native_api_base_url = None
            raise ConnectionError('Error in parameters base_url and api_version')

    def _request(self, method, endpoint, **kwarg):
        url = '{0}{1}'.format(self.native_api_base_url, endpoint)
        if 'auth' in kwarg:
            auth = kwarg['auth']
            del kwarg['auth']
        else:
            auth = False
        if auth:
            if self.api_token:
                if 'params' not in kwarg:
                    kwarg['params'] = {}
                kwarg['params']['key'] = self.api_token
            else:
                DataverseError('{0}: no API token for {1}'.format(method, url))
        try:
            if 'debug' in kwarg:
                debug = True
                del kwarg['debug']
            else:
                debug = False
            if 'metadata' in kwarg:
                metadata = kwarg['metadata']
                if isinstance(metadata, dict):
                    payload = json.dumps(metadata)
                elif isinstance(metadata, str):
                    payload = metadata
                else:
                    raise DataverseError('Metadata must be str of dict, not {}'.\
                                         format(str(type(metadata))))
                del kwarg['metadata']
            else:
                payload = {}
            if debug:
                print('!!! kwarg={}'.format(kwarg))
            response = method_callable[method](url, data=payload, **kwarg)
            # print('response.json={}'.format(response.json()))
            code = response.status_code
            code_class = code // 100
            # 1: informational response, caller should decide what to do
            # 2: success
            # 4: client error, caller should handle this class of error
            if code_class in [1, 2, 4]:
                return response
            elif code_class in [3, 5]: # redirection or server error
                message = response.json()['message']
                raise DataverseError('{0}: HTTP error {1} - {2}: {3}'.\
                                     format(method, response.status_code, url, message))
            else: # this should never occur
                raise DataverseError('{}: unexpected status code {} for {}'.\
                                     format(method, code, url))
        except ConnectionError:
            print('{}: could not create connection {}'.format(method, url))
            sys.exit(1)

    def get_request(self, endpoint, **kwarg):
        return self._request('GET', endpoint, **kwarg)
    def delete_request(self, endpoint, **kwarg):
        return self._request('DELETE', endpoint, **kwarg)
    def post_request(self, endpoint, **kwarg):
        return self._request('POST', endpoint, **kwarg)
    def put_request(self, endpoint, **kwarg):
        return self._request('PUT', endpoint, **kwarg)

    def get_dataverse(self, identifier, auth=False):
        endpoint = '/dataverses/{0}'.format(identifier)
        response = self.get_request(endpoint, auth=auth)
        # print(response.json())
        return Dataverse(connection=self, data=response.json()['data'])

    def get_dataset(self, identifier, is_pid=False, auth=True):
        if is_pid:
            endpoint = '/datasets/:persistentId/?persistentId={0}'.format(identifier)
        else:
            endpoint = '/datasets/{0}'.format(identifier)
        response = self.get_request(endpoint, auth=auth)
        # print(response.json())
        return Dataset(connection=self, data=response.json()['data'])