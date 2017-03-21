#!/usr/bin/python2
# cm_ansible: create cluster with using cloudera manager API

DOCUMENTATION = '''
---
module: create_cluster
short_description: Create cloudera manager clustercluster
description:
    - Create a cluster
options:
    cm_host:
      description:
        - Cloudera Manager hostname.
      required: true
      default: null
    cm_port:
      description:
        - Cloudera Manager port.
      required: false
      default: 7180
    cm_username:
      description:
        - Cloudera Manager user.
      required: true
      default: null
    cm_password:
      description:
        - Cloudera Manager password.
      required: true
      default: null
    cdh_version:
      description:
        - CDH major version.
      required: false
      default: null
    cluster_name:
      description:
        - Cluster name.
      required: true
      default: cluster01
'''

EXAMPLES = '''
# Create mycluster in CM
- create_cluster:
    cm_host: cm.example.com
    cm_username: admin
    cm_password: my-password
    state: present
    cluster_name: mycluster
  register: cm

'''

import os
import time
import syslog
import sys
from ansible.module_utils.basic import *

try:
    from cm_api.api_client import *
    from cm_api import *
    from cm_api.endpoints.cms import ClouderaManager
    from cm_api.endpoints.types import config_to_json, ApiConfig
    CM_API = True
except ImportError:
    CM_API = False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            cm_host=dict(required=True, type='str'),
            cm_port=dict(required=False, type='int', default=7180),
            cm_username=dict(required=True, type='str'),
            cm_password=dict(required=True, type='str', no_log=True),
            cm_tls=dict(required=False, type='bool', default=False),
            cm_version=dict(required=False, type='int', default=10),
            cdh_version=dict(required=False, type='str'),
            cluster_name=dict(required=False, type='str',default='cluster01'),
            state=dict(default='present',
                       choices=['present', 'absent'])
        )
    )

    cm_host = module.params.get('cm_host')
    cm_port = module.params.get('cm_port')
    cm_username = module.params.get('cm_username')
    cm_password = module.params.get('cm_password')
    cm_tls = module.params.get('cm_tls')
    cm_version = module.params.get('cm_version')
    cdh_version = module.params.get('cdh_version')
    cluster_name = module.params.get('cluster_name')
    state = module.params.get('state')

    changed = False

    if not CM_API:
        module.fail_json(changed=changed, msg='cm_api required for this module')

    try:
        api = ApiResource(cm_host, server_port=cm_port,
                                  username=cm_username,
                                  password=cm_password,
                                  use_tls=cm_tls,
                                  version=cm_version)
        cms = ClouderaManager(api)
    except ApiException as e:
        module.fail_json(changed=changed,
                         msg="Can't connect to CM API: {0}".format(e))


    if state == "present":
        try:
          api.create_cluster(cluster_name,version=cdh_version)
          module.exit_json(changed=True, rc=0)
        except Exception as e:
          module.fail_json(changed=changed, msg="{0}".format(e))
    elif state == "absent":
        try:
          api.delete_cluster(cluster_name)
          module.exit_json(changed=True, rc=0)
        except Exception as e:
            module.fail_json(changed=False, msg="{0}".format(e))
    module.exit_json(changed=False, settings=cms.get_config('summary'))

if __name__ == '__main__':
        main()
