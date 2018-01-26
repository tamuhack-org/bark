import math
import sys
from pymongo.errors import BulkWriteError
from bson.objectid import ObjectId

class PyMongoHandler(object):
    def __init__(self, mongo_db):
        self.mongo_db = mongo_db

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
        for index, person_data in enumerate(data_list):
            bulk.find({"email": person_data["email"]}).upsert().update({'$set': person_data})
        try:
            result = bulk.execute()
            return {"uploads": result["nInserted"] + result["nUpserted"], "repeats": result["nModified"]}
        except BulkWriteError as bwe:
            print ("Unexpected error " + bwe.details)

    def _internal_delete(self, query, is_single=True):
        if is_single:
            delete_result = self.mongo_db.db.applicants.delete_one(query)
        else:
            delete_result = self.mongo_db.db.applicants.delete_many(query)
        return {"deleted": delete_result.deleted_count}

    def save(self, data_list):
        list_formatted = [self.generate_document(i) for i in data_list]
        return self._internal_save(list_formatted)

    def delete(self, input_dict, single=True):
        return self._internal_delete(input_dict, is_single=single)

    def generate_document(self, input_dict):
        save_dict = {}
        for key in self.typeform_mapping.values():
            save_dict[key] = ""
        for key, value in input_dict.iteritems():
            if key in save_dict: save_dict[key] = value
        return save_dict

    def get_applicant(self, query):
        return self.mongo_db.db.applicants.find_one(query)
    
    def accept_applicant(self, person_id):
        return self.mongo_db.db.applicants.update_one({"_id":ObjectId(person_id)}, {"$set":{"status": "accepted"}})

    def reject_applicant(self, person_id):
        return self.mongo_db.db.applicants.update_one({"_id":ObjectId(person_id)}, {"$set":{"status": "rejected"}})

    def clear_applicant_status(self, person_id):
        return self.mongo_db.db.applicants.update_one({"_id":ObjectId(person_id)}, {"$set":{"status": ""}})

    def delete_all(self):
        pass

