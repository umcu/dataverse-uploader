from requests import get, put, post
import json

verbose = True # set this to False if you prefer less output

method_callable = {
    'GET': get, 'PUT': put, 'POST': post
}

class Api:
    def __init__(self, base_url, api_token):
        self.base_url = base_url
        self.api_token = api_token
        self.headers = {'X-Dataverse-key': api_token, 'Content-Type': 'application/json'}

    def __str__(self):
        return f"Api(url='{self.base_url}', key='{self.api_token}')"

    """An HTTP request results in a response.
    Each response has a 3-digit status code.
    The first digit determines the reponse class:
        1: informational response, caller should decide what to do
        2: success
        3: redirection error
        4: client error, caller should handle this class of error 
        5: server error
    """

    def _request(self, method, endpoint, **kwarg):
        if 'props' in kwarg:
            props = kwarg['props']
            del kwarg['props']
            if isinstance(props, dict):
                payload = json.dumps(props)
                if verbose: print("Props: "+json.dumps(props, indent=2, sort_keys=True))
            elif isinstance(props, str):
                payload = props
                if verbose: print(f"Props: {props}")
            else:
                raise ValueError(f"props must be str or dict, not {type(props)}")
        else:
            payload = ''
        completed_endpoint = endpoint.format(url=self.base_url, **kwarg)
        response = method_callable[method](completed_endpoint, data=payload, headers=self.headers)
        code = response.status_code
        code_class = code // 100
        if code_class in [1, 2, 4]:
            resp_json = response.json()
            if 'data' in resp_json:
                if verbose:
                    print(resp_json['data'])
                return resp_json['data']
            else:
                print(f"{method} {completed_endpoint} -> code {code}")
                print(f"no data property in {resp_json}")
                return []
        elif code_class in [3, 5]:
            resp_json = response.json()
            if 'message' in resp_json:
                message = resp_json['message']
                print(message)
            else:
                print(f"{method} {completed_endpoint} -> code {code}")
                print(f"no message property in {resp_json}")
            return []
        else:
            print(f"{method} {completed_endpoint} -> unexpected status code {code}")
            return []

    def get_request(self, endpoint, **kwarg):
        return self._request('GET', endpoint, **kwarg)

    def post_request(self, endpoint, **kwarg):
        return self._request('POST', endpoint, **kwarg)

    def put_request(self, endpoint, **kwarg):
        return self._request('PUT', endpoint, **kwarg)

    def dataverse_create(self, dataverse_id, name, alias, email):
        contacts = [{'contactEmail': f'{elt}@umcutrecht.nl'} for elt in email.split(',')]
        props = {'name': name, 'alias': alias, 'dataverseContacts': contacts,
                 'affiliation': 'UMCU', 'description': '', 'dataverseType': 'DEPARTMENT'}
        return self.post_request("{url}/api/dataverses/{dvid}", dvid=dataverse_id, props=props)

    def dataverse_publish(self, dataverse_id):
        return self.post_request("{url}/api/dataverses/{dvid}/actions/:publish", dvid=dataverse_id)

    def dataverse_view(self, dataverse_id):
        return self.get_request("{url}/api/dataverses/{dvid}", dvid=dataverse_id)

    def dataverse_contents(self, dataverse_id):
        return self.get_request("{url}/api/dataverses/{dvid}/contents", dvid=dataverse_id)

    def dataverse_groups(self, dataverse_id):
        return self.get_request("{url}/api/dataverses/{dvid}/groups", dvid=dataverse_id)

    def dataverse_add_group(self, dataverse_id, name, alias, description):
        props = {'displayName': name, 'aliasInOwner': alias, 'description': description}
        return self.post_request("{url}/api/dataverses/{dvid}/groups", dvid=dataverse_id, props=props)

    def dataverse_roles(self, dataverse_id):
        return self.get_request("{url}/api/dataverses/{dvid}/assignments", dvid=dataverse_id)

    def dataverse_add_role(self, dataverse_id, assignee, role):
        props = {'assignee': assignee, 'role': role}
        return self.post_request("{url}/api/dataverses/{dvid}/assignments", dvid=dataverse_id, props=props)

    def dataset_create(self, dataverse_id, props):
        """Add new dataset to this dataverse. The metadata should be in a dictionary `props` that
        is derived from on the file `dataset-minimal-metadata.json` (see Dataverse API documentation).`"""
        return self.post_request("{url}/api/dataverses/{dvid}/datasets", dvid=dataverse_id, props=props)
