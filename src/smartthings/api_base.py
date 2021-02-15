import requests
from attrdict import AttrDict

import re
import os
import urllib.parse
import logging

from pprint import pprint

mlog = logging.getLogger(__name__)


class SmartResponse(object):
    def __init__(self, response):
        self.response = response
        self._json_decoded = None
        try:
            self._json_decoded = self.response.json()
        except Exception as e:
            # can't decode, we'll suppress
            raise e

    def __int__(self):
        return self.response.status_code

    def __str__(self):
        return self.response.content

    def __getitem__(self, key):
        if self._json_decoded is None:
            raise KeyError(key)
        return self._json_decoded[key]

    def copy(self):
        return self.response.json()

    def has_key(self, key):
        return key in self._json_decoded

    def keys(self):
        return self._json_decoded.keys()

    def values(self):
        return self._json_decoded.values()

    def items(self):
        return self._json_decoded.items()

    def __contains__(self, item):
        return item in self._json_decoded

    def __iter__(self):
        return iter(self._json_decoded)

    @property
    def is_ok(self):
        return self.response.status_code == 200

    @property
    def error(self):
        return AttrDict(self._json_decoded['error'])


class SmartThingsClient(object):
    _api_base = 'https://api.smartthings.com/v1'

    def __init__(self, url=None, **kwargs):
        # Provide either a token with 'token' or:
        #   a 'tokenfile' name AND optionally a 'tokenfilepath' list of dirnames to search
        self._token = None
        self._session = requests.Session()

        # updating the token has a side-effect of updating the session auth header!
        if 'token' in kwargs:
            self.token = kwargs['token']
        elif 'tokenfile' in kwargs:
            get_token_args = { 'filename': kwargs['tokenfile'] }
            if 'tokenfilepath' in kwargs:
                get_token_args['search_path'] = kwargs['tokenfilepath']

            self.token = SmartThingsClient.get_token(**get_token_args)
        else:
            self.token = None

        # custom API base URLs
        if url is None:
            self.url = self._api_base
        else:
            self.url = url

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        match = re.search('^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', token)
        if not match:
            raise ValueError("Token '{}' is not in the correct format".format(token))

        self._token = token
        self._session.headers.update({'Authorization': 'Bearer ' + self._token})

    @staticmethod
    def get_token(filename='access_token.secret',
                  search_path=['.', os.getenv('HOME', '.')]):
        token = None
        for path in search_path:
            mlog.debug("Looking for '{}' in '{}'".format(filename, path))
            fullname = os.path.join(path, filename)
            if os.path.exists(fullname):
                with open(fullname, 'r') as f:
                    token = f.read().strip()

                match = re.search('^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', token)
                if match:
                    mlog.info("Token Loaded from '{}'".format(fullname))
                    return token

        return token

    def _request(self, method, endpoint, endpoint_args=None, params=None, data=None, **kwargs):
        real_endpoint = endpoint
        if endpoint_args is not None:
            real_endpoint = endpoint.format(**endpoint_args)

        call_url = urllib.parse.urljoin(self.url, real_endpoint)

        request_args = {}
        if params is not None:
            request_args['params'] = params
        if data is not None:
            request_args['json'] = data
        request_args.update(kwargs)

        request = self._session.prepare_request(
            requests.Request(method, call_url, **request_args)
        )

        return SmartResponse(self._session.send(request))

    def list_devices(self, capability=None, capability_mode="and"):
        return self._request('GET', 'devices', params={
            'capability': capability,
            'capabilityMode': capability_mode
        })

    def describe_device(self, device_id):
        return self._request('GET', 'devices/{deviceId}', {'deviceId': device_id})

    def device_status(self, device_id, component_id='main'):
        return self._request('GET',
                             '/devices/{deviceId}/components/{componentId}/status',
                             {'deviceId': device_id, 'componentId': component_id})

    def switch(self, device_id, state):
        return self._request('POST',
                             'devices/{deviceId}/commands',
                             {'deviceId': device_id},
                             data={
                                'commands': [{
                                    'capability': "switch",
                                    'command': state
                                }]
                             })
