import requests
import re
from random import randint

DEFAULT_REQUEST_LIMIT = 1000

class Typeform_Parser(object):
    def __init__(self, values, typeform_mapping, request_str):
        # assign this based on out specific typeform configuration
        self.schema = {}
        #mapping between field_id(in input) and id
        self.fd_to_id = {}
        self.typeform_config = typeform_mapping
        # here, we build a schema based on values that want to be used in "app.py" and the specific configuration
        for value in values:
            for k, v in self.typeform_config.items():
                if value is v:
                    self.schema[k] = v
        self.request_string = request_str
        self.data = []

    #initialize field id table
    def _init_fd(self, data):
        if not self.fd_to_id:
            for elem in data["questions"]:
                if str(elem["field_id"]) not in self.fd_to_id:
                    self.fd_to_id[str(elem["field_id"])] = elem["id"]
        
    def parse_preview(self):
        data = requests.get(self.request_string).json()
        self._init_fd(data)
        responses = data["responses"]
        limit, count = data["stats"]["responses"]["showing"], data["stats"]["responses"]["total"]
        if not limit: return None
        request_data = {}
        while not request_data:
            request_data = responses[randint(0, limit)]["answers"]
        return {"data": self._convert_to_schema(request_data, data), "count": count}

    def parse_data(self):
        output = []
        data = requests.get(self.request_string).json()
        num_entries = data["stats"]["responses"]["total"]
        if not num_entries: return None
        limit = min(num_entries, DEFAULT_REQUEST_LIMIT)
        iter_num = (num_entries // limit) + 1
        for request_range in range(0, iter_num):
            # mult request range by 1000 and make it an offset in the typeform request for each iteration
            print request_range * DEFAULT_REQUEST_LIMIT
            responses = requests.get(self.request_string +"&offset=" + str(request_range * DEFAULT_REQUEST_LIMIT)).json()["responses"]
            for response in responses:
                entry = response["answers"]
                if entry: output.append(self._convert_to_schema(entry, data))
        return output

    def _convert_to_schema(self, answer_dict, request_body):
        output_dict = {}
        self._init_fd(request_body)
        for key, value in self.typeform_config.iteritems():
            if key != "custom" and self.fd_to_id[key] in answer_dict:
                output_dict[self.typeform_config[key]] = answer_dict[self.fd_to_id[key]]
            elif key == "custom":
                output_dict[self.typeform_config[key]] = ""
        return output_dict

    def get_count(self):
        return self._get_metadata()["total"]
