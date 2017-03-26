import csv

#creating a parser class that will hold a schema and also take in the csv data from the textbox on the "upload" template
class Parser():
    #note: the schema will be lrge tuple of string, specified by the user
    def __init__(self, input_schema = {}):
        #schema is a list of keys that are specified by the user
        self.schema = input_schema 

    def process_txt(self, input_data):
        #approach: basically, take this data, and output a list of dictionaries that can be placed into mongo
        #we will take care of repeats by using the mongo "insert" function
        output = []  
        for item in input_data.splitlines():
            newdic = {}
            processed = item.split(',')
            for x in range(len(processed)):
                processed[x] = processed[x].strip('"')
                if x in self.schema:
                    newdic[self.schema[x]] = processed[x]
            output.append(newdic)
        return output

    def process_csv(self, input_data):
        pass

schema_dict = {0: "id", 1: "first_name",2: "last_name", 3: "gender", 5: "email", 6: "phone", 7: "school", 8: "school_year", 10: "major", 11:"resume", 13: "travel_method", 15: "hackathon_experience", 16: "shirt", 18: "race", 26: "submission_date"}
p = Parser(schema_dict)
sample_data = """13f4cc3c003894dd20343c6cd8f55593,Nate,Graf,Male,,nategraf@tamu.edu,9403681054,"Texas A & M University-College Station",Senior,,"Computer Engineering",,https://admin.typeform.com/form/results/file/download/HDv04s/28158536/b692c7efdab6-Resume___TAMU_Hack.pdf,Walking,,"4 - 7",M,,"White or Caucasian",,"https://nategraf.github.io/(All other relevant things link from there)","A block-chain based implementations of an a market for physical goods (like Craigslist). This system would include methods of artificial intelligence to match suppliers with customers, enable bartering and transaction verification. Of course this would require time be be quite abundant as well.
In the span of one TAMU Hack,  I might seek to build a VR origami trainer which interactively guides the user through folding actual origami. ","Surface Pro 4",1,,"2016-08-22 15:04:30","2016-08-22 15:19:41",2945c8a327"""
print p.process_txt(sample_data)
        

#we need to take araw text, treat it as a csv, and parse it into several python  dictionaries
# def process_csv(input_data):
    # filename = input("What is the name of the file you want me to parse?") 
    # for testing purposes irl we will read from configobj
    # try:
        # with open(filename) as csvfile: 
            # reader = csv.DictReader(csvfile)
            # for row in reader:
                # person = process_row(row)
                # # write hacker to database (probably with a method like: insert_person(person))
    # except OSError:
        # print("File not found.")
# # called on each row to create a Person object from it. we can make database calls here but we could put it in another function (which I think would be better) - Denise
# def process_row(response):
    # #create Person object
    # # Im not doing it now bc I bet the constructor for person will change a lot
    # # Should look like:
    # # hacker = Person(response['first_name'], response['last_name']) <- The keys in parenthesis are whatever the first row of the csv is
    # # we could/should consider using kwargs or something
    # return None # will return Person object here
# process_csv()
