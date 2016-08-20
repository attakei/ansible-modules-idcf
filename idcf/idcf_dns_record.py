#!/usr/bin/python
# -*- coding:utf8 -*-

DOCUMENTATION = '''
---
module: idcf_dns_recode
short_description: Manage IDCF-cloud DNS record
version_added: "2.1"
author: "attakei, @attakei"
'''

EXAMPLES = '''
# Simply usage
- idcf_dns_record:
    idcf_api_key: YOUR_API_KEY
    idcf_secret_key: YOU_SECRET_KEY
    zone: example.com
    name: www
    type: A
    content: 127.0.0.1
  register: result
- debug: var=result.record
'''

RETURN = '''
zone:
    description: Record information
    returned: success
    type: dict
    sample: {
        "uuid": "e46466a6-377c-4b5a-84b2-f93f3a8d09eb",
        "name": "www.example.com",
        "type": "A",
        "content": "192.168.1.1",
        "ttl": 3600,
        "created_at": "2015-08-01T00:00:00+09:00",
        "updated_at": null,
        "priority": null
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
        'zone': { 'required': True, },
        'name': { 'required': True, },
        'content': { 'required': True, },
        'type': { 'required': True, },
        'state': { 'required': False, 'default': 'present', 'choices': ['present', 'absent']},
    }
    module = AnsibleModule(argument_spec=argument_spec)
    # Proceed
    client = IDCFAPiClient(module.params['idcf_api_key'], module.params['idcf_secret_key'])
    zone = fetch_zone(client, module.params['zone'])

    # No action
    if zone is None:
        module.fail_json(msg='Zone is not found')

    records_url = '/zones/{}/records'.format(zone['uuid'])
    resp = client.request('GET', records_url)
    zone_detail = json.loads(resp.read())
    if module.params['name'] == '@':
        record_domain = module.params['zone']
    else:
        record_domain = '{}.{}'.format(module.params['name'], module.params['zone'])
    record = None
    for record_ in zone_detail:
        if record_['name'] == record_domain:
            record = record_
            break

    # No action
    if record is None and module.params['state'] == 'absent':
        module.exit_json(changed=False, zone={}, msg='Record is not already exists.')

    # Create new record
    if record is None and module.params['state'] == 'present':
        payload = {
            'name': record_domain,
            'type': module.params['type'],
            'content': module.params['content'],
            'ttl': zone['default_ttl'],
        }
        resp = client.request('POST', records_url, data=payload)
        if resp.status != 201:
            module.fail_json(status_code=resp.status, msg=resp.reason)
        module.exit_json(changed=True, record=json.loads(resp.read()))

    # Updade record if params is changed
    if record is not None and module.params['state'] == 'present':
        record_url = '{}/{}'.format(records_url, record['uuid'])
        payload = {}
        if module.params['content'] != record['content']:
            payload['content'] = module.params['content']
        if len(payload) == 0:
            # Not changed
            module.exit_json(changed=False, zone=zone, msg='Not changed')
        resp = client.request('PUT', record_url, data=payload)
        if resp.status != 200:
            module.fail_json(status_code=resp.status, msg=resp.reason)
        module.exit_json(changed=True, zone=json.loads(resp.read()))

    # Delete current record
    if record is not None and module.params['state'] == 'absent':
        record_url = '{}/{}'.format(records_url, record['uuid'])
        resp = client.request('DELETE', record_url)
        if resp.status != 200:
            module.fail_json(status_code=resp.status, msg=resp.reason)
        module.exit_json(changed=True, record=json.loads(resp.read()))

    # Others
    module.fail_json(msg='Fatal error', xxx=record)


from ansible.module_utils.basic import *


if __name__ == '__main__':
    main()
