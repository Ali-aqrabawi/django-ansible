from django.db import models
from dj_ansible import const

"""
Bases
"""


class BaseAnsibleGroup(models.Model):
    name = models.CharField(max_length=100)
    ansible_connection = models.CharField(choices=const.ANSIBLE_CONNECTION_CHOICES, max_length=100)

    class Meta:
        abstract = True


class BaseAnsibleDeviceGroup(BaseAnsibleGroup):
    ansible_become = models.BooleanField(default=False)

    class Meta:
        abstract = True


class BaseAnsibleHost(models.Model):
    host = models.CharField(max_length=100)
    ansible_ssh_host = models.GenericIPAddressField()
    ansible_user = models.CharField(max_length=100)
    ansible_ssh_pass = models.CharField(max_length=100)

    class Meta:
        abstract = True


"""
Groups Models
"""


class AnsibleNetworkGroup(BaseAnsibleDeviceGroup):
    ansible_network_os = models.CharField(choices=const.ANSIBLE_NETWORK_OS_CHOICES, max_length=100)
    parent_group = models.ForeignKey('self', on_delete=models.DO_NOTHING, related_name='child_group',
                                     null=True, blank=True)

    class Meta:
        db_table = 'ansible_network_groups'
        app_label = 'dj_ansible'


class AnsibleServerGroup(BaseAnsibleDeviceGroup):
    parent_group = models.ForeignKey('self', on_delete=models.DO_NOTHING, related_name='child_group',
                                     null=True, blank=True)

    class Meta:
        db_table = 'ansible_server_groups'
        app_label = 'dj_ansible'


class AnsibleAWSGroup(BaseAnsibleGroup):
    ami = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    sshkey = models.CharField(max_length=100)
    vpcid = models.CharField(max_length=100)

    class Meta:
        db_table = 'ansible_aws_groups'
        app_label = 'dj_ansible'


"""
Hosts Models
"""


class AnsibleNetworkHost(BaseAnsibleHost):
    ansible_become_pass = models.CharField(max_length=100)
    group = models.ForeignKey(AnsibleNetworkGroup, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'ansible_network_hosts'
        app_label = 'dj_ansible'


class AnsibleServerHost(BaseAnsibleHost):
    ansible_become_pass = models.CharField(max_length=100)
    group = models.ForeignKey(AnsibleServerGroup, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'ansible_server_hosts'
        app_label = 'dj_ansible'
