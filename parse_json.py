import json
import math
from pprint import pprint

DEFAULT_FILE_NAME = "laptop_test_data_mega.json"


class TestCalculator:
    test_data = None
    markers = {
        "filter_size": {},
        "symmetric_difference": {},
        "a_value": {},
        "max_hashes": {}
    }

    def read_json_file(self, filename=DEFAULT_FILE_NAME):
        with open(filename, "r") as json_file:
            self.test_data = json.loads(json_file.read())

    def recalculate_success_rates(self, test_name="mega_test", table_name="IBLT"):
        for iteration in self.test_data[table_name][test_name].keys():
            try:
                counter = 0
                for message in self.test_data[table_name][test_name][iteration]["success_messages"]:
                    if message[2] is True:
                        counter += 1
                self.test_data[table_name][test_name][iteration]["success_rate"] = \
                    counter / len(self.test_data[table_name][test_name][iteration]["success_messages"])
            except KeyError:
                continue

    def generate_data_ranges(self, test_name="mega_test", table_name="ALOHA"):
        for iteration in self.test_data[table_name][test_name].keys():
            try:
                for marker in self.markers.keys():
                    if self.test_data[table_name][test_name][iteration][marker] not in self.markers[marker].keys():
                        self.markers[marker][self.test_data[table_name][test_name][iteration][marker]] = {}
            except KeyError:
                continue

    def display_results(self, test_name="mega_test", table_name="IBLT"):
        test_log = []
        markers = self.markers.copy()

        for test_iteration in self.test_data[table_name][test_name].keys():
            try:
                if self.test_data[table_name][test_name][test_iteration]["success_rate"] > 0:

                    for key in markers.keys():
                        if self.test_data[table_name][test_name][test_iteration]["success_rate"] not in \
                                markers[key][self.test_data[table_name][test_name][test_iteration][key]].keys():

                            markers[key][self.test_data[table_name][test_name][test_iteration][key]][
                                self.test_data[table_name][test_name][test_iteration]["success_rate"]
                            ] = []

                        markers[key][self.test_data[table_name][test_name][test_iteration][key]][
                            self.test_data[table_name][test_name][test_iteration]["success_rate"]
                        ].append(self.test_data[table_name][test_name][test_iteration].copy())
                    # test_log.append({"test_number": test_iteration,
                    #                  "results": self.test_data[table_name][test_name][test_iteration].copy(),
                    #                  "table_name": table_name})

            except KeyError:
                pass
        return markers.copy()

    def print_json(self):
        print(self.test_data.keys())


if __name__ == '__main__':
    tc = TestCalculator()
    tc.read_json_file()
    tc.generate_data_ranges()

    results = {"IBLT": [], "RIBLT": [], "ALOHA": []}

    for table_name in results.keys():
        # tc.recalculate_success_rates(table_name=table_name)
        results[table_name] = tc.display_results(table_name=table_name)

    data_info = {"IBLT": {}, "RIBLT": {}, "ALOHA": {}}

    for table_name in results.keys():
        for metric in results[table_name].keys():
            for metric_value in results[table_name][metric].keys():
                for success_rate in results[table_name][metric][metric_value].keys():
                    result_count = len(results[table_name][metric][metric_value][success_rate])
                    metrics = {
                        "filter_size": {"min": math.inf,
                                        "max": -math.inf},
                        "symmetric_difference": {"min": math.inf,
                                                 "max": -math.inf},
                        "a_value": {"min": math.inf,
                                    "max": -math.inf},
                        "max_hashes": {"min": math.inf,
                                       "max": -math.inf}
                    }
                    for result in results[table_name][metric][metric_value][success_rate]:
                        for field in metrics.keys():

                            if result[field] < metrics[field]["min"]:
                                metrics[field]["min"] = result[field]
                            if result[field] > metrics[field]["max"]:
                                metrics[field]["max"] = result[field]

                    data_info[table_name]["%s: %s, Success: %s, Count: %s" %
                                          (metric, metric_value, success_rate, result_count)] = {
                        "table_name": table_name,
                        "metric": metric,
                        "success_rate": success_rate,
                        "successes": result_count,
                        "edge_values": metrics.copy()
                    }

    with open("quick_result_parse.json", "w") as save_file:
        save_file.write(json.dumps(results))

    with open("quick_metric_parse.json", "w") as save_file:
        save_file.write(json.dumps(data_info))

    # with open("quick_result_parse.csv", "w") as save_file:
    #     save_file.write("table_name,filter_size,symmetric_difference,max_hashes,a_value\n")
    #     for table_name in results.keys():
    #         for entry in results[table_name]:
    #             save_file.write("%s,%s,%s,%s,%s,%s\n" % (table_name, entry["results"]["filter_size"],
    #                                                      entry["results"]["symmetric_difference"],
    #                                                      entry["results"]["max_hashes"],
    #                                                      entry["results"]["a_value"],
    #                                                      entry["results"]["success_rate"]))
