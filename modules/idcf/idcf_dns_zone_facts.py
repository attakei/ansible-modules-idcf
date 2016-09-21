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
    client = DNSClient(module.params['idcf_api_key'], module.params['idcf_secret_key'])
    resp = client.request('GET', '/zones')
    module.exit_json(changed=False, zones=json.loads(resp.read()))


from ansible.module_utils.basic import *
from ansible.module_utils.idcf import DNSClient


if __name__ == '__main__':
    main()
