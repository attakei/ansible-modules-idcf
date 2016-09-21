# -*- coding:utf8 -*-
"""Ansible module utils for IDCF-cloud
"""


import time
import hmac
from base64 import b64encode
from httplib import HTTPSConnection
from ansible.module_utils.basic import *


class DNSClient(object):
    """IDCF-cloud DNS service API client
    """
    HOSTNAME = 'dns.idcfcloud.com'
    BASE_PATH = '/api/v1'
    DEFAULT_EXPIRES = 60

    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def generate_signature(self, method, path, expires):
        base_string = '\n'.join([
            method, path, self.api_key, str(expires), ''
        ])
        hash = hmac.new(self.secret_key, base_string, AVAILABLE_HASH_ALGORITHMS['sha256'])
        return b64encode(hash.digest())

    def request(self, method, path, data=None, expires=60):
        expires = int(time.time()) + expires
        path = self.BASE_PATH + path
        signature = self.generate_signature(method, path, expires)
        headers = {
            'X-IDCF-APIKEY': self.api_key,
            'X-IDCF-Expires': expires,
            'X-IDCF-Signature': signature,
        }
        conn = HTTPSConnection(self.HOSTNAME)
        if data is None:
            conn.request(method, path, headers=headers)
        else:
            headers['Content-Type'] = 'application/json'
            conn.request(method, path, body=json.dumps(data), headers=headers)
        return conn.getresponse()
