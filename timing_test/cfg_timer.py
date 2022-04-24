from timing_test.timer import Timer
from typing import Union


class CFGTimer(Timer):

    def generate_varying_input_data_for_test(self):
        for i in range(1, self.settings.max_depth + 1):
            yield {'depth': i}

    def add_result_to_results(self, run_index: int, algorithm_name: str, result: Union[str, float], **input_data):
        if result == self.settings.timeout_key or self.results[algorithm_name][input_data['depth'] - 1] == self.settings.timeout_key:
            self.results[algorithm_name][input_data['depth'] - 1] = self.settings.timeout_key
        else:
            self.results[algorithm_name][input_data['depth'] - 1] += result

    def aggregate_results(self, algorithm_name: str, **input_data):
        self.results[algorithm_name][input_data['depth'] - 1] = round(
            self.results[algorithm_name][input_data['depth'] - 1] / (self.settings.re_runs * len(self.tests)), 3)

    def has_timed_out_before(self, algorithm_name: str, **input_data) -> bool:
        if self.results[algorithm_name][input_data['depth'] - 1] == self.settings.timeout_key:
            return True
        if input_data['depth'] - 2 >= 0 and self.results[algorithm_name][input_data['depth'] - 2] == self.settings.timeout_key:
            return True
        return False
