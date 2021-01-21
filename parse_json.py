import json
import math
import traceback
from pprint import pprint
import sqlite3

DEFAULT_FILE_NAME = "test_data_mega.json"
DATABASE_FILE = "test_results.db"


class TestCalculator:
    test_data = None
    markers = {"IBLT": {
        "filter_size": {},
        "symmetric_difference": {},
        "a_value": {},
        "max_hashes": {}},
        "RIBLT": {
            "filter_size": {},
            "symmetric_difference": {},
            "a_value": {},
            "max_hashes": {}},
        "ALOHA": {
            "filter_size": {},
            "symmetric_difference": {},
            "a_value": {},
            "max_hashes": {}},
    }

    def read_json_file(self, filename=DEFAULT_FILE_NAME):
        with open(filename, "r") as json_file:
            self.test_data = json.loads(json_file.read())
        print(len(self.test_data["IBLT"]["mega_test"]))
        print(len(self.test_data["RIBLT"]["mega_test"]))
        print(len(self.test_data["ALOHA"]["mega_test"]))

    def recalculate_success_rates(self, test_name="mega_test", table_name="IBLT"):
        for iteration in self.test_data[table_name][test_name].keys():
            try:
                counter = 0
                for message in self.test_data[table_name][test_name][iteration]["success_messages"]:
                    if message[2] is True:
                        counter += 1
                self.test_data[table_name][test_name][iteration]["success_rate"] = \
                    counter / len(self.test_data[table_name][test_name][iteration]["success_messages"])
            except KeyError as e:
                print("%s for recalc_success with %s" % (e, table_name))
                pass

    def generate_data_ranges(self, test_name="mega_test", table_name="ALOHA"):
        for iteration in self.test_data[table_name][test_name].keys():
            try:
                for marker in self.markers[table_name].keys():
                    if marker == "total_tests":
                        continue
                    if self.test_data[table_name][test_name][iteration][marker] not in self.markers[table_name][
                        marker].keys():
                        self.markers[table_name][marker][self.test_data[table_name][test_name][iteration][marker]] = {}
            except KeyError as e:
                print("%s at data_ranges for %s" % (e, table_name))
                pass

    def display_results(self, test_name="mega_test", table_name="IBLT", min_success_rate=.2):
        test_log = []
        markers = self.markers.copy()

        for test_iteration in self.test_data[table_name][test_name].keys():
            try:
                if self.test_data[table_name][test_name][test_iteration]["success_rate"] >= min_success_rate:

                    for key in markers[table_name].keys():
                        if key == "total_tests":
                            continue
                        if self.test_data[table_name][test_name][test_iteration] != {} and \
                                self.test_data[table_name][test_name][test_iteration]["success_rate"] not in \
                                markers[table_name][key][
                                    self.test_data[table_name][test_name][test_iteration][key]].keys():
                            markers[table_name][key][self.test_data[table_name][test_name][test_iteration][key]][
                                self.test_data[table_name][test_name][test_iteration]["success_rate"]
                            ] = []

                        markers[table_name][key][self.test_data[table_name][test_name][test_iteration][key]][
                            self.test_data[table_name][test_name][test_iteration]["success_rate"]
                        ].append(self.test_data[table_name][test_name][test_iteration].copy())
                    test_log.append({"test_number": test_iteration,
                                     "results": self.test_data[table_name][test_name][test_iteration].copy(),
                                     "table_name": table_name})

            except KeyError as e:
                # print("%s at disp_res for %s" % (e, table_name))
                traceback.print_exc()
        return markers[table_name]  # , test_log.copy(), len(self.test_data[table_name][test_name])

    def print_json(self):
        print(self.test_data.keys())

    def load_test_file(self, filename=DEFAULT_FILE_NAME):
        self.read_json_file(filename)
        return self.test_data.copy()


def parse_results():
    tc.read_json_file()

    results = {"IBLT": {}, "RIBLT": {}, "ALOHA": {}}
    results_log = {"IBLT": {}, "RIBLT": {}, "ALOHA": {}}

    for bloom_table_name in ["RIBLT"]:  # results.keys():
        tc.generate_data_ranges(table_name=bloom_table_name)
        # tc.recalculate_success_rates(table_name=bloom_table_name)
        # results[bloom_table_name], results_log[bloom_table_name], results[bloom_table_name]["total_tests"] = \
        tc.display_results(table_name=bloom_table_name)

    results = tc.markers.copy()

    data_info = {"IBLT": {}, "RIBLT": {}, "ALOHA": {}}

    for bloom_table_name in results.keys():
        for metric in results[bloom_table_name].keys():
            if metric == "total_tests":
                continue
            for metric_value in results[bloom_table_name][metric].keys():
                for success_rate in results[bloom_table_name][metric][metric_value].keys():
                    result_count = len(results[bloom_table_name][metric][metric_value][success_rate])
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
                    for result in results[bloom_table_name][metric][metric_value][success_rate]:
                        for field in metrics.keys():

                            if result[field] < metrics[field]["min"]:
                                metrics[field]["min"] = result[field]
                            if result[field] > metrics[field]["max"]:
                                metrics[field]["max"] = result[field]

                    data_info[bloom_table_name]["%s: %s, Success: %s, Count: %s" %
                                                (metric, metric_value, success_rate, result_count)] = {
                        "table_name": bloom_table_name,
                        "metric": metric,
                        "success_rate": success_rate,
                        "successes": result_count,
                        "edge_values": metrics.copy()
                    }

    with open("quick_result_parse.json", "w") as save_file:
        save_file.write(json.dumps(results))

    with open("high_success_results_only.json", "w") as save_file:
        save_file.write(json.dumps(data_info))
    # with open("quick_metric_parse.json", "w") as save_file:
    #     save_file.write(json.dumps(data_info))

    # with open("quick_result_parse.csv", "w") as save_file:
    #     save_file.write("table_name,filter_size,symmetric_difference,max_hashes,a_value\n")
    #     for table_name in results.keys():
    #         for entry in results[table_name]:
    #             save_file.write("%s,%s,%s,%s,%s,%s\n" % (table_name, entry["results"]["filter_size"],
    #                                                      entry["results"]["symmetric_difference"],
    #                                                      entry["results"]["max_hashes"],
    #                                                      entry["results"]["a_value"],
    #                                                      entry["results"]["success_rate"]))


def results_to_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("""CREATE TABLE IF NOT EXISTS BloomTableType(
                        name        varchar(40),
                        PRIMARY KEY (name) ) """)
    try:
        cursor.execute("""INSERT INTO BloomTableType(name) VALUES(?)""", ['IBLT'])
        cursor.execute("""INSERT INTO BloomTableType(name) VALUES(?)""", ['RIBLT'])
        cursor.execute("""INSERT INTO BloomTableType(name) VALUES(?) """, ['ALOHA'])
    except (SyntaxError, sqlite3.IntegrityError):
        pass

    cursor.execute(""" CREATE TABLE IF NOT EXISTS TestData(
                            name                    varchar(40),
                            test_no                 integer,
                            set_size                float,
                            filter_size             float,
                            average_creation_time   float,
                            average_comparison_time float,
                            reported_success_rate   float,
                            verified_success_rate   float,
                            symmetric_difference    float,
                            a_value                 float,
                            max_hashes              integer,
                            PRIMARY KEY             (name, test_no),
                            CONSTRAINT              name
                             FOREIGN KEY            (name)
                             REFERENCES             BloomTableType(name)
                                                    ON UPDATE CASCADE
                                                    ON DELETE CASCADE) """)
    conn.commit()

    results = tc.load_test_file()

    for t_name in results.keys():
        for test_no in results[t_name]["mega_test"].keys():
            try:
                success_rate = 0
                for success_message in results[t_name]["mega_test"][test_no]["success_messages"]:
                    if success_message[2] is True:
                        success_rate += 1
                success_rate = success_rate / len(results[t_name]["mega_test"][test_no]["success_messages"])
                conn.execute("""INSERT INTO TestData VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (t_name, test_no,
                                                          results[t_name]["mega_test"][test_no]["set_size"],
                                                          results[t_name]["mega_test"][test_no]["filter_size"],
                                                          results[t_name]["mega_test"][test_no][
                                                                                           "average_creation_time"],
                                                          results[t_name]["mega_test"][test_no][
                                                                                           "average_comparison_time"],
                                                          success_rate,
                                                          results[t_name]["mega_test"][test_no]["success_rate"],
                                                          results[t_name]["mega_test"][test_no]["symmetric_difference"],
                                                          results[t_name]["mega_test"][test_no]["a_value"],
                                                          results[t_name]["mega_test"][test_no]["max_hashes"]))
            except (sqlite3.IntegrityError, KeyError) as e:
                print(str(e))
    conn.commit()


tc = None

if __name__ == '__main__':
    tc = TestCalculator()
    # parse_results()
    results_to_database()
