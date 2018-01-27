import math
import sys
from pymongo.errors import BulkWriteError
from bson.objectid import ObjectId

class PyMongoHandler(object):
    def __init__(self, mongo_db, input_required, additional_params):
        self.mongo_db = mongo_db
        self.required = input_required
        self.params = additional_params

    def get_paginated_entries(self, page_size=10, page_num=1, query_phrase={}):
        entries = self.entries(query_phrase)
        skips, num_pages = page_size * (page_num - 1), int(math.ceil(float(entries.count())/page_size))
        cursor = entries.skip(skips).limit(page_size)
        return {"page_num":page_num, "num_pages": num_pages,"entries":[x for x in cursor]}

    def count(self):
        return self.mongo_db.db.applicants.count()

    def entries(self, filter_dict={}):
        return self.mongo_db.db.applicants.find(filter_dict)

    def _internal_save(self, data_list):
        bulk = self.mongo_db.db.applicants.initialize_unordered_bulk_op()
        data_list = [self.convert2unicode(elem) for elem in data_list]
        print data_list
        for index, person_data in enumerate(data_list):
            bulk.find({"email": person_data["email"]}).upsert().update({'$set': person_data})
        try:
            result = bulk.execute()
            return {"uploads": result["nInserted"] + result["nUpserted"], "repeats": result["nModified"]}
        except BulkWriteError as bwe:
            print ("Unexpected error " + bwe.details)

    def convert2unicode(self, mydict):
        for k, v in mydict.iteritems():
            if isinstance(v, str):
                mydict[k] = unicode(v, errors='replace')
        return mydict

    def _internal_delete(self, query, is_single=True):
        if is_single:
            delete_result = self.mongo_db.db.applicants.delete_one(query)
        else:
            delete_result = self.mongo_db.db.applicants.delete_many(query)
        return {"deleted": delete_result.deleted_count}

    def save(self, data_list):
        list_validated = [self.generate_document(i) for i in data_list]
        return self._internal_save(list_validated)

    def delete(self, input_dict, single=True):
        return self._internal_delete(input_dict, is_single=single)

    def generate_document(self, input_dict):
        for value in self.required:
            if value not in input_dict:
                error_string = "Missing the following value in a record: " + value
                raise ValueError(error_string)
        for value in self.params:
            if value not in input_dict:
                input_dict[value] = ""
        return input_dict

    def get_applicant_by_id(self, person_id):
        return self.mongo_db.db.applicants.find_one({"_id":ObjectId(person_id)})
    
    def checkin_applicant(self, person_id):
        return self.mongo_db.db.applicants.update_one({"_id":ObjectId(person_id)}, {"$set":{"checked_in": "true"}})

    def uncheck_applicant(self, person_id):
        return self.mongo_db.db.applicants.update_one({"_id":ObjectId(person_id)}, {"$set":{"checked_in": ""}})

    def update_applicant_info(self, person_id, info_str):
        return self.mongo_db.db.applicants.update_one({"_id":ObjectId(person_id)}, {"$set":{"additional": info_str}})

    def update_applicant_reimbursement(self, person_id, reimbursement_str):
        return self.mongo_db.db.applicants.update_one({"_id":ObjectId(person_id)}, {"$set":{"travel_reimbursement": reimbursement_str}})

    def delete_all(self):
        pass

