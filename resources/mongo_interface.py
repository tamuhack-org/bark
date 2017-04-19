import flask_mongoengine

db = flask_mongoengine.MongoEngine()


# creating a simple Person Class
class Person(db.DynamicDocument):
    # note: it looks like a dynamic field requires a "require" attribute
    email = db.StringField(required=True)


class Test_Person(db.DynamicDocument):
    # note: it looks like a dynamic field requires a "require" attribute
    email = db.StringField(required=True)


class DB_Handler(object):
    def __init__(self, person_class, values):
        self.person_db = person_class
        self.values = values

    def _internal_save(self, data_list):
        # store the number os succesful uploads that happen
        num_uploads = 0
        # also store the number of repeats
        num_repeat = 0
        for person_data in data_list:
            if not self.person_db.objects(email=person_data["email"]):
                p = self.person_db()
                for x in person_data:
                    setattr(p, x, person_data[x])
                p.save()
                num_uploads += 1
            else:
                num_repeat += 1
        return {"uploads": num_uploads, "repeats": num_repeat}

    # save group and save single both return a tuple with the number of uploads followed by the number of repeats
    def save_group(self, data_list):
        return self._internal_save(data_list)

    def save_single(self, dict):
        output_dict = {}
        # build a dictionary using the schema that is defined and fill it with provided fields
        for value in self.values:
            if value in dict:
                output_dict[value] = dict[value]
            else:
                output_dict[value] = ""
        # pass a list of one element to the internal save method
        return self._internal_save([output_dict])

    def delete_single(self, email):
        to_delete = self.person_db.objects(email=email)
        num_delete = 0
        if to_delete:
            to_delete.delete()
            num_delete = 1
        return {"deleted": num_delete}

    def delete_all(self):
        for person in self.person_db.objects():
            person.delete()
