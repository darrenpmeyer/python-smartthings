from .api_base import *

import requests
import urllib.parse
import os
import re

from pprint import pprint, pformat

API_BASE = "https://api.smartthings.com/v1"


def get_token(filename='access_token.secret',
              search_path=['.', os.getenv('HOME', '.')]):
    token = None
    for path in search_path:
        fullname = os.path.join(path, filename)
        if os.path.exists(fullname):
            with open(fullname, 'r') as f:
                token = f.read().strip()

            match = re.search('^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', token)
            if match:
                print("Token Loaded from '{}'".format(fullname))
                return token

    return token


def get_request(access_token, url, params={}, **kwargs):
    headers = {'Authorization': 'Bearer ' + access_token}
    pprint(headers)
    return requests.get(url, params=params, headers=headers, **kwargs)


def post_request(access_token, url, data={}, **kwargs):
    headers = {'Authorization': 'Bearer ' + access_token}
    pprint(headers)
    return requests.post(url, json=data, headers=headers, **kwargs)


def device_switch(access_token, deviceID, state="on", capability="switch", base_url=API_BASE, endpoint="devices/{deviceID}/commands"):
    call_url = urllib.parse.urljoin(base_url, endpoint.format(deviceID=deviceID))
    response = post_request(access_token, call_url, data={
        'commands': [{
            'capability': capability,
            'command': state
        }]
    })
    return response
