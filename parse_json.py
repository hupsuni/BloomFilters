import json
from pprint import pprint

DEFAULT_FILE_NAME = "server_test_data_mega.json"


class TestCalculator:
    test_data = None
    markers = {
        "filter_size": [],
        "symmetric_difference": [],
        "a_value": [],
        "max_hashes": []
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
        for iteration in self.test_data[table_name][test_name]:
            try:
                for marker in self.markers.keys():
                    if iteration[marker] not in self.markers[marker]:
                        self.markers[marker].append(iteration[marker])
            except KeyError:
                continue

    def display_results(self, test_name="mega_test", table_name="IBLT"):
        test_log = []
        markers = {
            "filter_size": [],
            "symmetric_difference": [],
            "a_value": [],
            "max_hashes": []
        }
        # previous_success_rate = 0
        for test_iteration in self.test_data[table_name][test_name].keys():
            # counter = 0
            try:
                # for message in self.test_data[table_name][test_name][test_iteration]["success_messages"]:
                #     if message[2] is True:
                #         counter += 1
                # success_rate = counter / len(self.test_data[table_name][test_name][test_iteration]["success_messages"])
                if self.test_data[table_name][test_name][test_iteration]["success_rate"] > 0:

                    if self.test_data[table_name][test_name][test_iteration]["filter_size"] \
                            not in markers["filter_size"] or \
                            self.test_data[table_name][test_name][test_iteration]["symmetric_difference"] \
                            not in markers["symmetric_difference"] or \
                            self.test_data[table_name][test_name][test_iteration]["a_value"] \
                            not in markers["a_value"] or \
                            self.test_data[table_name][test_name][test_iteration]["max_hashes"] \
                            not in markers["max_hashes"]:

                        for key in markers.keys():
                            markers[key].append(self.test_data[table_name][test_name][test_iteration][key])
                        test_log.append({"test_number": test_iteration,
                                         "results": self.test_data[table_name][test_name][test_iteration].copy(),
                                         "table_name": table_name})

                    # previous_success_rate = success_rate
            except KeyError:
                pass
        return test_log

    def print_json(self):
        print(self.test_data.keys())


if __name__ == '__main__':
    tc = TestCalculator()
    tc.read_json_file()

    results = {"IBLT": [], "RIBLT": [], "ALOHA": []}

    for table_name in results.keys():
        tc.recalculate_success_rates(test_name=table_name)
        results[table_name] = tc.display_results(table_name=table_name)

    with open("quick_result_parse.json", "w") as save_file:
        save_file.write(json.dumps(results))

    pprint(results)
    with open("quick_result_parse.csv", "w") as save_file:
        save_file.write("table_name,filter_size,symmetric_difference,max_hashes,a_value\n")
        for table_name in results.keys():
            for entry in results[table_name]:
                save_file.write("%s,%s,%s,%s,%s,%s\n" % (table_name, entry["results"]["filter_size"],
                                                         entry["results"]["symmetric_difference"],
                                                         entry["results"]["max_hashes"],
                                                         entry["results"]["a_value"],
                                                         entry["results"]["success_rate"]))
