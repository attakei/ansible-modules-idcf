#!/usr/bin/python
# -*- coding:utf8 -*-

DOCUMENTATION = '''
---
module: idcf_dns_zone
short_description: Manage IDCF-cloud DNS zone
version_added: "2.1"
author: "attakei, @attakei"
'''

EXAMPLES = '''
# Simply usage
- idcf_dns_zone: idcf_api_key=YOUR_API_KEY idcf_secret_key=YOU_SECRET_KEY name=example.com email: example@example.com
  register: result
- debug: var=result.zone
'''

RETURN = '''
zone:
    description: Zone information
    returned: success
    type: dict
    sample: {
        "uuid": "80ef4bb8-f915-47fa-9e12-5f3b8ce6e181",
        "name": "example.com",
        "default_ttl": 30000,
        "created_at": "2015-08-01T00:00:00+09:00",
        "updated_at": null,
        "description": "my zone",
        "authenticated": false
    }
'''


import time
import hmac
from base64 import b64encode
from httplib import HTTPSConnection


class IDCFAPiClient(object):
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


def fetch_zone(client, zone_name):
    resp = client.request('GET', '/zones')
    zones = json.loads(resp.read())
    for zone in zones:
        if zone['name'] == zone_name:
            return zone
    return None


def main():
    # Define module settings
    argument_spec = {
        'idcf_api_key': { 'required': True, },
        'idcf_secret_key': { 'required': True, },
        'name': { 'required': True, },
        'email': { 'required': False, },
        'description': { 'required': False, 'default': 'My zone', },
        'default_ttl': { 'required': False, 'default': 30000, 'type': 'int' },
        'state': { 'required': False, 'default': 'present', 'choices': ['present', 'absent']},
    }
    module = AnsibleModule(argument_spec=argument_spec)
    # Proceed
    client = IDCFAPiClient(module.params['idcf_api_key'], module.params['idcf_secret_key'])
    zone = fetch_zone(client, module.params['name'])

    # No action
    if zone is None and module.params['state'] == 'absent':
        module.exit_json(changed=False, zone={}, msg='Zone is not already exists.')

    # Delete zone
    if zone is not None and module.params['state'] == 'absent':
        resp = client.request('DELETE', '/zones/'+zone['uuid'])
        if resp.status != 200:
            module.fail_json(status_code=resp.status, msg=resp.reason)
        module.exit_json(changed=True, zone={})

    # Create new zone
    if zone is None and module.params['state'] == 'present':
        payload = {
            'name': module.params['name'],
            'email': module.params['email'],
            'description': module.params['description'],
            'default_ttl': module.params['default_ttl'],
        }
        resp = client.request('POST', '/zones', data=payload)
        if resp.status != 201:
            module.fail_json(status_code=resp.status, msg=resp.reason)
        module.exit_json(changed=True, zone=json.loads(resp.read()))

    # Updade zone if params is changed
    if zone is not None and module.params['state'] == 'present':
        payload = {}
        if module.params['description'] != zone['description']:
            payload['description'] = module.params['description']
        if module.params['default_ttl'] != zone['default_ttl']:
            payload['default_ttl'] = module.params['default_ttl']
        if len(payload) == 0:
            # Not changed
            module.exit_json(changed=False, zone=zone, msg='Not changed')
        resp = client.request('PUT', '/zones/'+zone['uuid'], data=payload)
        if resp.status != 200:
            module.fail_json(status_code=resp.status, reason=resp.reason)
        module.exit_json(changed=False, zone=json.loads(resp.read()))

    # Others
    module.fail_json(msg='Fatal error')


from ansible.module_utils.basic import *


if __name__ == '__main__':
    main()
