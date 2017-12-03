import math

class PyMongoHandler(object):
    def __init__(self, mongo_db, typeform_mapping):
        self.mongo_db = mongo_db
        self.typeform_mapping = typeform_mapping

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
        num_uploads, num_repeats = 0, 0
        for person_data in data_list:
            print person_data
            if self.mongo_db.db.applicants.count({"email": person_data["email"]}):
                num_repeats += 1
            else:
                self.mongo_db.db.applicants.insert_one(person_data)
                num_uploads += 1
        return {"uploads": num_uploads, "repeats": num_repeats}

    def _internal_delete(self, query={}, is_single=True):
        if is_single:
            num_delete = self.mongo_db.db.applicants.delete_one(query)
        else:
            num_delete = self.mongo_db.db.applicants.delete_many(query)
        return {"deleted": num_delete}

    def save_group(self, data_list):
        list_update = [self.generate_document(i) for i in data_list]
        return self._internal_save(list_update)

    def save_single(self, input_dict):
        dict_to_save = self.generate_document(input_dict)
        print dict_to_save
        return self._internal_save([dict_to_save])

    def delete_single(self, input_dict):
        return self._internal_delete(input_dict, is_single=True)

    def generate_document(self, input_dict):
        save_dict = {}
        for key in self.typeform_mapping.values():
            save_dict[key] = ""
        for key, value in input_dict.iteritems():
            if key in save_dict: save_dict[key] = value
        return save_dict



        # output_dict = {}
        # # build a dictionary using the schema that is defined and fill it with provided fields
        # for value in self.values:
        #     if value in dict:
        #         output_dict[value] = dict[value]
        #     else:
        #         output_dict[value] = ""
        # # pass a list of one element to the internal save method
        # return self._internal_save([output_dict])

        # to_delete = self.person_db.objects(email=email)
        # num_delete = 0
        # if to_delete:
        #     to_delete.delete()
        #     num_delete = 1
        # return {"deleted": num_delete}

    def delete_all(self):
        pass
        # for person in self.person_db.objects():
        #     person.delete()
