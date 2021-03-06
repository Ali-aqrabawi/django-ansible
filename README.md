# Django-Ansible
![PyPI - Status](https://img.shields.io/pypi/status/django-ansible.svg)
![PyPI](https://img.shields.io/pypi/v/django-ansible.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-ansible.svg)
![PyPI - Django Version](https://img.shields.io/pypi/djversions/django-ansible.svg)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/7f726043dc76428cb553c726ca388c5f)](https://www.codacy.com/app/Ali-aqrabawi/django-ansible?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Ali-aqrabawi/django-ansible&amp;utm_campaign=Badge_Grade)
![GitHub](https://img.shields.io/github/license/ali-aqrabawi/django-ansible.svg)

dj_ansible is a Django App that allow Django applications to integrate with Ansible.
basiclly it allow you to store inventory data in database using DjangoModels, and provide 
an API to execute Json-like playbooks.

`currently supported on Ansible <= 2.7.10`

## Quick Start

 1. install django-ansible

    `pip install django-ansible`

 2. Add "dj_ansible" to your INSTALLED_APPS setting like this

        INSTALLED_APPS = [
           ...
           'dj_ansible',
        ]
 3. Run `python manage.py makemigrations` to create migrations for the tables.
 
 4. Run `python manage.py migrate` to create the needed tables.

 5. add your inventory data to two tables
     - ansible_network_groups (model: `AnsibleNetworkGroup()`)
     - ansible_network_hosts (model: `AnsibleNetworkHost()`)
    
     like following :
    
        from dj_ansible.models import AnsibleNetworkHost,AnsibleNetworkGroup

        my_group = AnsibleNetworkGroup(name='cisco_firewalls',
                                       ansible_connection='network_cli',
                                       ansible_network_os='asa',
                                       ansible_become=True)
        my_group.save()
        host = AnsibleNetworkHost(host='my_asa',
                                  ansible_ssh_host='192.168.1.1',
                                  ansible_user='admin',
                                  ansible_ssh_pass='pass',
                                  ansible_become_pass='pass',
                                  group=my_group)
        host.save()
 
 ## Running Play-books
  to run play-books use the `execute` API to execute your play-books
 
 ### Example
 
 1. create play-book dictionary

         my_play = dict(
                   name="may_first_play",
                   hosts='cisco_firewalls',
                   become='yes',
                   become_method='enable',
                   gather_facts='no',
                   tasks=[
                       dict(action=dict(module='asa_command', commands=['show version','show ip'])),
                       dict(action=dict(module='asa_config', lines=['network-object host 10.1.0.1'])
                   ]
               )

 2.  run `my_play` using the `execute` API

         from dj_ansible.ansible_kit import execute
          
         result = execute(my_play)
         # print the stats
         print(json.dumps(result.stats, indent=4))
         # print execution results
         print(json.dumps(result.results, indent=4))

 3. the `result` object consist of two jsons:

  - first `state`, which look like this:

        {
        "all_ok": false,
        "total_hosts": 3,
        "has_changed": false,
        "duration": 12.400323867797852,
        "hosts_stats": {
            "ok_hosts": {
                "count": 2,
                "hosts": [
                    "fw2",
                    "fw1"
                ]
            },
            "failed_hosts": {
                "count": 1,
                "hosts": [
                    "ios_switch1"
                ]
            },
            "processed_hosts": {
                "count": 3,
                "hosts": [
                    "fw2",
                    "fw1",
                    "ios_switch1"
                ]
            },
            "changed_hosts": {
                "count": 0,
                "hosts": []
            }
        },
        "hosts": [
            {
                "host": "fw2",
                "status": "ok",
                "changed": false
            },
            {
                "host": "fw1",
                "status": "ok",
                "changed": false
            },
            {
                "host": "ios_switch1",
                "status": "failed",
                "changed": false
            }
        ]}

  - and `result`, which looks like this:

        {
        "failed": [
            {
                "host": "ios_switch1",
                "tasks": [
                    {
                        "name": "asa_command",
                        "result": {
                            "msg": "timed out",
                            "_ansible_no_log": false
                        }
                    }
                ]
            }
        ],
        "success": [
            {
                "host": "fw2",
                "tasks": [
                    {
                        "name": "asa_command",
                        "result": {
                            "invocation": {
                                "module_args": {
                                    "username": null,
                                    "authorize": null,
                                    "password": null,
                                    "passwords": null,
                                    "context": null,
                                    "retries": 10,
                                    "auth_pass": null,
                                    "interval": 1,
                                    "commands": [
                                        "show version"
                                    ],
                                    "host": null,
                                    "ssh_keyfile": null,
                                    "timeout": null,
                                    "provider": null,
                                    "wait_for": null,
                                    "port": null,
                                    "match": "all"
                                }
                            },
                            "stdout_lines": [
                                [
                                    "Cisco Adaptive Security Appliance Software Version 9.5(3)6 ",
                                    "Device Manager Version 7.1(3)",
                                    ....
                                    "Configuration last modified by enable_15 at 12:55:31.479 EDT Sun Apr 7 2019"
                                ]
                            ],
                            "changed": false,
                            "stdout": [
                                "Cisco Adaptive Security Appliance Software Version 9.5(3)6 \nDevice Manager Version 7.1(3)\n\n... ],
                            "_ansible_parsed": true,
                            "_ansible_no_log": false
                        }
                    }
                ]
            },
            {
                "host": "fw1",
                "tasks": [
                    {
                        "name": "asa_command",
                        "result": {
                            "invocation": {
                                "module_args": {
                                    "username": null,
                                    "authorize": null,
                                    "password": null,
                                    "passwords": null,
                                    "context": null,
                                    "retries": 10,
                                    "auth_pass": null,
                                    "interval": 1,
                                    "commands": [
                                        "show version"
                                    ],
                                    "host": null,
                                    "ssh_keyfile": null,
                                    "timeout": null,
                                    "provider": null,
                                    "wait_for": null,
                                    "port": null,
                                    "match": "all"
                                }
                            },
                            "stdout_lines": [
                                [
                                    "Cisco Adaptive Security Appliance Software Version 9.1(7)16 ",
                                    "",
                                    "Compiled on Thu 30-Mar-17 17:39 by builders",
                                    "System image file is \"disk0:/asa917-16-k8.bin\"",
                                    "Config file at boot was \"startup-config\"",
                                    "",
                                    ....
                                    "Configuration register is 0x1",
                                    "Configuration last modified by admin at 16:25:49.318 UTC Sat Apr 6 2019"
                                ]
                            ],
                            "changed": false,
                            "stdout": [
                                "Cisco Adaptive Security Appliance Software Version 9.1(7)16 \n\n.... ],
                            "_ansible_parsed": true,
                            "_ansible_no_log": false
                        }
                    }
                ]
            }
        ]}
  
#### Note
for now dj_ansible support network devices inventory only, contibution is so welcome to add support for other
inventories types like servers.
