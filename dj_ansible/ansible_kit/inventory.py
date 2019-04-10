from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from dj_ansible.models import AnsibleNetworkGroups, AnsibleHosts
from dj_ansible.exceptions import DjangoAnsibleError


class _Inventory(InventoryManager):
    """Collect Inventory from DB"""

    def __init__(self):
        loader = DataLoader()
        self.host_model = AnsibleHosts
        self.network_group_model = AnsibleNetworkGroups
        super(_Inventory, self).__init__(loader)

    def _add_group_childes(self, group):
        if group.parent_group:
            if group.parent_group.name not in self._inventory.groups:
                self._inventory.add_group(group.parent_group.name)
            self._inventory.add_child(group.parent_group.name, group.name)
            self._add_group_childes(group.parent_group)

    def _parse_network_groups(self, groups):
        try:
            for group in groups:
                self._inventory.add_group(group.name)

                for field in group._meta.fields:
                    field_name = field.name
                    if field_name == 'parent_group':
                        continue
                    value = getattr(group, field.name)
                    if value:
                        self._inventory.set_variable(group.name, field_name, value)
                self._add_group_childes(group)
            hosts = self.host_model.objects.all()
            for host in hosts:
                self._inventory.add_host(host.host, group=host.group.name)

                for field in host._meta.fields:
                    field_name = field.name
                    value = getattr(host, field.name)
                    if value:
                        self._inventory.set_variable(host.host, field_name, value)
        except Exception as e:
            raise DjangoAnsibleError(str(e))

    def parse_sources(self, cache=False):
        groups = self.network_group_model.objects.all()
        self._parse_network_groups(groups)


def get_inventory():
    inventory = _Inventory()

    return inventory
