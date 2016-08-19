#!/usr/bin/python
# -*- coding:utf8 -*-

DOCUMENTATION = '''
---
# If a key doesn't apply to your module (ex: choices, default, or
# aliases) you can use the word 'null', or an empty list, [], where
# appropriate.
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
    module = AnsibleModule({

    })
    # Proceed
    module.exit_json()


from ansible.module_utils.docker_common import *


if __name__ == '__main__':
    main()
