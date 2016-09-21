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
    client = DNSClient(module.params['idcf_api_key'], module.params['idcf_secret_key'])
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
from ansible.module_utils.idcf import DNSClient


if __name__ == '__main__':
    main()
