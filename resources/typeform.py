import requests
import json
import re
from random import randint
from math import *
import flask_mongoengine


class Typeform_Parser(object):
    def __init__(self, p_class):
        self.schema = {"28125773": "first_name", "28125775": "last_name",
                      "28125781": "gender", "28127706": "travel",
                      "28127225": "additional", "28125780": "experience",
                      "28127904": "major", "28125779": "email",
                      "28141455": "race", "28125778": "number",
                      "28128125":"school", "28158536": "resume"}
        self.request_string = "https://api.typeform.com/v1/form/HDv04s?key=598bae62949ccf0f2098d86db19592d0aa0a2260"
        self.data = []
        self.person_db = p_class
        #initialize the attributes of the person object

    def save_data(self):
        data_list = self._return_data("data")
        for person_data in data_list:
            try:
                #if the person object exists with a given email, ignore it
                self.person_db.objects.get(email=person_data["email"])
                print person_data["email"]
            except Exception:
                #if we get a "does not exist", create a new person
                p = self.person_db()
                for x in person_data:
                    setattr(p, x, person_data[x])
                p.save()

    def _return_data(self, preview):
        output = []
        num_entries = self.get_entry_count()
        upper = 1000
        if not num_entries:
            return None
        if preview is not "preview":
            upper = int(ceil(num_entries*.001)*1000)
        for request_range in range(0, upper, 1000):
            r = requests.get(self.request_string+"&offset="+str(request_range))
            dict = json.loads(r.text)
            responses = dict["responses"]
            #responses may be empty, so we check here
            for x in responses:
                #the answers section is the part that we actually want
                entry = x["answers"]
                #if the entry part is full (Not full means that the application wasn't finished)
                if entry:
                    #create a new dictionary
                    curr_dic = {}
                    for x,y in entry.iteritems():
                        #check to see if the value has something in it
                        if y:
                            #get rid of all
                            x = re.sub("[^0-9]", "", x)
                            #if there exists a key in schema that is a part of our current key
                            if x in self.schema:
                                curr_dic[self.schema[x]] = y
                    output.append(curr_dic)
        if preview is "preview":
            return output[randint(0,len(output))]
        return output

    def get_preview(self):
        return self._return_data("preview")

    def get_data(self):
        return self._return_data("data")

    def get_entry_count(self):
        r = requests.get(self.request_string)
        dict = json.loads(r.text)
        count = dict["stats"]["responses"]["total"]
        return int(count)
