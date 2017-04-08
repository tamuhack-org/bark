import unittest
from resources import typeform
from app import VALUES

class TestCase(unittest.TestCase):
    def setUp(self):
        self.test_parser = typeform.Typeform_Parser(VALUES)
        self.full_response = self.test_parser.parse_data()
        self.preview_response = self.test_parser.parse_preview()
        self.count = self.test_parser.get_count()
        self.schema_entries = self.test_parser.schema.values()

    # check that the response even exists and something comes of it
    def test_response_exists(self):
        #check that the response even exists and something comes of it
        self.assertNotEqual(0, len(self.full_response), "Response contains no data")

    # check that the response even exists and something comes of it
    def test_preview_exists(self):
        self.assertNotEqual(0, len(self.preview_response), "Preview contains no data")

    # confirm that all of the entries in the schema exist in a given typeform json person
    def test_response_contents(self):
        for person in self.full_response:
            for k,v in person.items():
                self.assertIn(k,self.schema_entries,"Extraneous data in response, check the response string")

    #check that the response contains the correct keys which exist in the schema that was built
    def test_preview_contents(self):
        schema_entries = self.test_parser.schema.values()
        for k,v in self.preview_response["data"].items():
            self.assertIn(k,schema_entries,"Extraneous data in preview, check the response string")

    #check that the count of the parsed data is less than or equal to the count stored in the json (no extra entries)
    def test_data_count(self):
        self.assertTrue(len(self.full_response) <= self.count, "The parsed response is larger than typeform count, extraneous data")

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()