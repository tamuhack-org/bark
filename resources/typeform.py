import requests
import re
from random import randint

DEFAULT_REQUEST_LIMIT = 1000

class Typeform_Parser(object):
    def __init__(self, config_dict):
        # assign this based on out specific typeform configuration
        # self.schema = {}
        # self.typeform_config = {"28125773": "first_name", "28125775": "last_name",
        #               "28125781": "gender", "28127706": "travel",
        #               "28127225": "additional", "28125780": "experience",
        #               "28127904": "major", "28125779": "email",
        #               "28141455": "race", "28125778": "number",
        #               "28128125":"school", "28158536": "resume"}
        # # here, we build a schema based on values that want to be used in "app.py" and the specific configuration
        # for value in values:
        #     for k, v in self.typeform_config.items():
        #         if value is v:
        #             self.schema[k] = v
        # print(self.schema)
        self.schema = config_dict

        self.request_string = "https://api.typeform.com/v1/form/HDv04s?key=598bae62949ccf0f2098d86db19592d0aa0a2260"
        self.data = []

    def parse_preview(self):
        # gets a python dictionary object from a get request
        data = requests.get(self.request_string).json()
        responses = data["responses"]
        total_count = data["stats"]["responses"]["total"]
        # return nothing if the count is 0
        if not total_count:
            return None
        # defines a limit for generating a random number
        limit = min(total_count, DEFAULT_REQUEST_LIMIT)
        # define an output, and continue to query random indexes until the output has a "non-empty" entry
        request_data = {}
        output_data = {}
        while not request_data:
            request_data = responses[randint(0, limit)]["answers"]
        # parses the "request_data" into a dictionary
        for k,v in request_data.items():
            # check to see if the value has something in it
            if v:
                # get rid of all extraneous numerals
                k = re.sub("[^0-9]", "", k)
                # if there exists a key in schema that is a part of our current key
                if k in self.schema:
                    output_data[self.schema[k]] = v
        while not output_data:
            output_data = responses[randint(0, limit)]["answers"]
        return {"data": output_data, "count": total_count}

    def parse_data(self):
        output = []
        num_entries = self._get_metadata()["total"]
        if not num_entries:
            return None
        #define a limit
        limit = min(num_entries, DEFAULT_REQUEST_LIMIT)
        #number of iterations or paginated requests
        iter = num_entries // limit + 1
        for request_range in range(0, iter):
            # mult request range by 1000 and make it an offset in the typeform request for each iteration
            responses = requests.get(self.request_string +"&offset=" + str(request_range * DEFAULT_REQUEST_LIMIT)).json()["responses"]
            #if the number of entries is less than 1000
            if responses:
                for response in responses:
                    # the answers section is the part that we actually want
                    entry = response["answers"]
                    # if the entry part is full (Not full means that the application wasn't finished)
                    if entry:
                        # create a new dictionary
                        curr_dic = {}
                        for k,v in entry.items():
                            # check to see if the value has something in it
                            if v:
                                # get rid of all
                                k = re.sub("[^0-9]", "", k)
                                # if there exists a key in schema that is a part of our current key
                                if k in self.schema:
                                    curr_dic[self.schema[k]] = v
                        output.append(curr_dic)
        return output

    def get_count(self):
        return self._get_metadata()["total"]
    #this method returns simple metadata for a the first page of a typeform request:
    #keywords are showing, total and completed

    def _get_metadata(self):
        r = requests.get(self.request_string)
        return r.json()["stats"]["responses"]

