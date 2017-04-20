import unittest
from flask import Flask
from resources import mongo_interface
from app import VALUES


# Things that this test should perform
# (1) input and delete a single entry
# -----attempt to overwrite an existing entry that has a
# (2) input and delete multiple entries
# (3) perform basic queries from the mongoengine library


class TestCase(unittest.TestCase):

    def setUp(self):
        # create a dummy flask instance to enable flask-mongoengine
        self.app = Flask(__name__)
        self.sample_doc = {"first_name": "John", "last_name": "Doe", "email": "john@doe.com"}
        self.emails = ["himank@himank.com", "denise@denise.com", "jay@jay.com", "julie@julie.com"]
        self.entries = []
        for email in self.emails:
            self.entries.append({"first_name": "Jay", "email": email})
        self.app.config['MONGODB_SETTINGS'] = {
            'db': 'm_engine_db',
            'host': 'mongodb://tamuhack17:Tamuhackdb17@ds129600.mlab.com:29600/m_engine_db'
        }
        # initialize the flask app (pass it to mongo)
        mongo_interface.db.init_app(self.app)
        # other necessary components:
        self.person_class = mongo_interface.Test_Person
        self.db_handler = mongo_interface.DB_Handler(self.person_class, VALUES)

    # test the upload/bring down of a single mongo document
    def test_single(self):
        # save the sample document
        response_1 = self.db_handler.save_single(self.sample_doc)
        # if the response of the save function or the number of documents in the db is not expected, error
        self.assertEqual(response_1, {"uploads":1, "repeats": 0}, "save response is incorrect")
        self.assertEqual(len(self.person_class.objects()), 1, "Documents existing prior to test, please drop-db")
        # delete the sample document from the db
        response_2 = self.db_handler.delete_single(self.sample_doc["email"])
        # check that the response and number of d elements is expected
        self.assertEqual(response_2, {"deleted": 1}, "delete response is incorrect")
        self.assertEqual(len(self.person_class.objects()), 0, "Document wasn't deleted")

    # attempt to overwrite an existing entry that already exists
    def test_overwrite(self):
        # save the same document twice and see if it's caught
        self.db_handler.save_single(self.sample_doc)
        response = self.db_handler.save_single(self.sample_doc)
        self.assertEqual(response, {"uploads": 0, "repeats": 1}, "overwrite response is incorrect")
        self.assertNotEqual(len(self.person_class.objects()), 2, "Both documents saved, no overwrite detected")
        # delete the entry
        self.db_handler.delete_single(self.sample_doc["email"])

    # attempt to add multiple to the db and delete them all
    def test_multiple(self):
        # add 4 entries to the database
        response = self.db_handler.save_group(self.entries)
        self.assertEqual(response, {"uploads": 4, "repeats": 0}, "multiple save response is incorrect")
        self.db_handler.delete_all()

    def tearDown(self):
        self.db_handler.delete_all()

if __name__ == '__main__':
    unittest.main()

