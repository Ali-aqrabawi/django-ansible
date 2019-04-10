from ansible.plugins.callback import CallbackBase
from collections import defaultdict


class ResultCallback(CallbackBase):
    """callback plugin used for collecting play results"""

    def __init__(self):
        self.results = defaultdict(list)
        self._host_tasts_dict = defaultdict(list)
        super(ResultCallback).__init__()

    def _is_host_in_result(self, host, key):
        for item in self.results[key]:
            if host in item.values():
                return True

    def _add_callback_result_to_results(self, result, status):
        host = result._host.name
        task_name = result.task_name
        task = {
            "name": task_name,
            "result": result._result
        }
        if not self._is_host_in_result(host, key='failed'):
            self.results[status].append({
                "host": host,
                "tasks": self._host_tasts_dict[host]
            })
        self._host_tasts_dict[host].append(task)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        """method to execute on failed execution"""
        self._add_callback_result_to_results(result, 'failed')
        self.custom_runner_on_failed(result, ignore_errors)

    def v2_runner_on_ok(self, result, **kwargs):
        """method to execute on Ok execution"""
        self._add_callback_result_to_results(result, 'success')
        self.custom_runner_on_ok(result, **kwargs)

    def custom_runner_on_failed(self, result, ignore_errors=False):
        pass

    def custom_runner_on_ok(self, result, **kwargs):
        pass
