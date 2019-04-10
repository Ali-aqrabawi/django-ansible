from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from dj_ansible.ansible_kit.inventory import get_inventory
from dj_ansible.exceptions import DjangoAnsibleError
from dj_ansible.ansible_kit.callback import ResultCallback
from collections import namedtuple
import time
import os

start = time.time()

os.environ['ANSIBLE_HOST_KEY_CHECKING'] = 'false'


class ExecutionResults:
    """an object to hold the play results and stats"""

    def __init__(self, stats, results, execution_time):
        self._stats = stats
        self._results = results
        self.execution_time = execution_time
        self._stats_dict = {}

        self.failed = []
        self.ok = []
        self.changed = []
        self.processed = []

        self.all_ok = False
        self.hosts = []
        self.total_hosts = 0
        self.has_change = False

        self._parse_hosts_stats()
        self._build_stats_dict()

    def _parse_hosts_stats(self):
        self.hosts = []
        self.failed = [host for host in self._stats.failures]
        self.ok = [host for host in self._stats.ok]
        self.changed = [host for host in self._stats.changed]
        self.processed = [host for host in self._stats.processed]

        for host in self.processed:
            host_dict = dict(host=host, status='failed', changed=False)
            if host in self.changed:
                host_dict['changed'] = True
            if host in self.ok:
                host_dict['status'] = 'ok'
            self.hosts.append(host_dict)

    def _build_stats_dict(self):
        all_ok = not self.failed
        has_changed = bool(self.changed)
        total_hosts = len(self.processed)

        ok_hosts = dict(count=len(self.ok), hosts=self.ok)
        failed_hosts = dict(count=len(self.failed), hosts=self.failed)
        processed_hosts = dict(count=len(self.processed), hosts=self.processed)
        changed_hosts = dict(count=len(self.changed), hosts=self.changed)

        hosts_stats = dict(ok_hosts=ok_hosts, failed_hosts=failed_hosts, processed_hosts=processed_hosts,
                           changed_hosts=changed_hosts)

        hosts = self.hosts

        self._stats_dict = dict(all_ok=all_ok, total_hosts=total_hosts, has_changed=has_changed,
                                duration=self.execution_time, hosts_stats=hosts_stats,
                                hosts=hosts)

    @property
    def stats(self):
        return self._stats_dict

    @property
    def results(self):
        return self._results


def execute(play_source, custom_callback=None, forks=10, connection='paramiko'):
    """
    run ansible play, and return result as json for the play.
    :param play_source: dict: play_book ex: dict(name="Ansible Play",
                                                 hosts=hosts,
                                                 become='yes',
                                                 become_method='enable',
                                                 gather_facts='no',
                                                 tasks=[
                                                    dict(action=dict(module='asa_command', commands=list(commands)), register='output'),
                                                    dict(action=dict(module='debug', args=dict(var='output')))
                                                 ]
                                                 )
    :param custom_callback: ResultCallback()
    :param forks: int:
    :param connection: str:
    :return: result: dict
    """
    Options = namedtuple('Options',
                         ['connection', 'module_path',
                          'forks', 'become', 'become_method', 'become_user', 'check', 'diff',
                          'ansible_host_key_checking'])
    options = Options(connection=connection, module_path=None, forks=forks, become=None, become_method=None,
                      become_user=None, check=False, diff=False, ansible_host_key_checking=False)

    call_back = custom_callback or ResultCallback()

    passwords = dict(vault_pass='secret')

    loader = DataLoader()

    inventory = get_inventory()
    variable_manager = VariableManager(loader=loader, inventory=inventory)

    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

    tqm = None

    try:
        tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            options=options,
            passwords=passwords,
            stdout_callback=call_back,

        )
        tqm.run(play)  # most interesting data for a play is actually sent to the callback's methods
    except Exception as e:
        raise DjangoAnsibleError(str(e))
    finally:
        # we always need to cleanup child procs and the structres we use to communicate with them
        result = call_back.results
        stats = tqm._stats
        exec_time = time.time() - start
        if tqm is not None:
            tqm.cleanup()
        return ExecutionResults(stats, result, exec_time)
