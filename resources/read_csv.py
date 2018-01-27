import csv

REQUIRED = ["first_name", "last_name", "email"]

class CsvHandler(object):
    def __init__(self, input_data, input_required):
        self.file_data = input_data
        self.required = input_required

    # generates a list of dictionary elemements that can be pushed to mongo
    def generate_documents(self):
        output = []
        reader = csv.reader(self.file_data)
        header = self._get_header(reader)
        for row in reader:
            document = {}
            for index, key in enumerate(header):
                document[key] = row[index]
            self._validate_document(document)
            output.append(document)
        return output

    # gets the header for a given csv, checking for duplicates and for required keys
    def _get_header(self, input_iterator):
        header_arr = []
        for value in next(input_iterator):
            if not value:
                self._assert_value_error("Empty header entry, not allowed")
            if value in header_arr: 
                self._assert_value_error("Duplicate key in input CSV header: " + value)
            header_arr.append(value)
        for key in self.required:
            if key not in header_arr:
                self._assert_value_error("Required key is missing in header: " + str(key))
        if not header_arr: 
            self._assert_value_error("Empty input CSV")
        return header_arr

    # checks that all required keys have proper values in each document
    def _validate_document(self, input_document):
        for key in self.required:
            if not input_document[key]:
                self._assert_value_error("Missing value for a required key for" + str(input_document))
    
    def _assert_value_error(self, error_str):
        raise ValueError(error_str)