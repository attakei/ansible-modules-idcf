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
    client = DNSClient(module.params['idcf_api_key'], module.params['idcf_secret_key'])
    zone = fetch_zone(client, module.params['zone'])

    if module.params['type'] not in ('A', ):
        module.fail_json(
            msg='"{}" type is not supported.'.format(module.params['type'])
        )
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
        if record_['name'] == record_domain \
        and record_['type'] == module.params['type'] \
        and record_['content'] == module.params['content']:
            record = record_
            break
    # On API record name
    record_domain = '{}.{}'.format(module.params['name'], module.params['zone'])

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
        module.exit_json(changed=False, zone={}, msg='Record is already exists.')

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
from ansible.module_utils.idcf import DNSClient


if __name__ == '__main__':
    main()
