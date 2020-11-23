# Created By Nick Huppert on 23/11/20.
import threading


class TSDict:
    _lock = threading.Lock()
    _instance = None

    @classmethod
    def instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls.__new__(cls)
                cls.results_dictionary = {
                    "IBLT": {

                    },
                    "ALOHA": {

                    },
                    "RIBLT": {

                    }
                }
        return cls._instance

    def set(self, table, key_string, field, value):
        try:
            self.get(table, key_string, field)
        except KeyError:
            with self._lock:
                self.results_dictionary[table][key_string] = {}
        finally:
            with self._lock:
                self.results_dictionary[table][key_string][field] = value

    def get(self, table, key_string, field):
        with self._lock:
            return self.results_dictionary[table][key_string][field]

    def get_all(self):
        with self._lock:
            return self.results_dictionary.copy()

