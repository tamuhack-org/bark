# I have tested this with a csv file from typeform - Denise

import csv

def process_csv():
    filename = input("What is the name of the file you want me to parse?") # for testing purposes irl we will read from configobj
    
    try:
        with open(filename) as csvfile: 
            reader = csv.DictReader(csvfile)
            for row in reader:
                person = process_row(row)
                # write hacker to database (probably with a method like: insert_person(person))
    except OSError:
        print("File not found.")
 
# called on each row to create a Person object from it. we can make database calls here but we could put it in another function (which I think would be better) - Denise
def process_row(response):
    #create Person object
    # Im not doing it now bc I bet the constructor for person will change a lot
    
    # Should look like:
    # hacker = Person(response['first_name'], response['last_name']) <- The keys in parenthesis are whatever the first row of the csv is
    # we could/should consider using kwargs or something
    return None # will return Person object here
    
process_csv()