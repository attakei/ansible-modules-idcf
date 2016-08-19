#!/usr/bin/python
# -*- coding:utf8 -*-

DOCUMENTATION = '''
---
module: idcf_dns_zone_facts
short_description: Retrieves IDCF-cloud DNS zones
version_added: "2.1"
author: "attakei, @attakei"
'''

EXAMPLES = '''
# Simply usage
- idcf_dns_zone_facts: idcf_api_key=YOUR_API_KEY idcf_secret_key=YOU_SECRET_KEY
  register: result
- debug: var=result.zones
'''

RETURN = '''
zones:
    description: List of zone information
    returned: always
    type: dict
    sample: [
        {
            "uuid": "80ef4bb8-f915-47fa-9e12-5f3b8ce6e181",
            "name": "example.com",
            "default_ttl": 30000,
            "created_at": "2015-08-01T00:00:00+09:00",
            "updated_at": null,
            "description": "my zone",
            "authenticated": false
        }
    ]
'''


import time
import hmac
from base64 import b64encode
from httplib import HTTPSConnection


class IDCFClient(object):
    """IDCF-cloud DNS service API client
    """
    HOSTNAME = 'dns.idcfcloud.com'
    BASE_PATH = '/api/v1'

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
        conn.request(method, path, headers=headers)
        resp = conn.getresponse()
        return json.loads(resp.read())


def main():
    # Define module settings
    argument_spec = {
        'idcf_api_key': {
            'required': True
        },
        'idcf_secret_key': {
            'required': True
        },
    }
    module = AnsibleModule(argument_spec=argument_spec)
    # Proceed
    client = IDCFClient(module.params['idcf_api_key'], module.params['idcf_secret_key'])
    zones = client.request('GET', '/zones')
    module.exit_json(changed=False, zones=zones)


from ansible.module_utils.docker_common import *


if __name__ == '__main__':
    main()
