class Person:
    def __init__(self, first_name = None):
        self.fname = first_name
        self.lname = None
        self.email = None

    def set_first(self, first):
        self.fname = first

    def set_last(self, last):
        self.lname = last

    def set_email(self, email):
        self.email = email
            
    def toDict(self):
        #returns a dictionsary with ifnromation for a given person
        return {"fname": self.fname, "lname": self.lname, "email": self.email}

    def fromDict(self, dic):
        #updates a given person based on an inputted dictionary
        self.fname = dic["fname"]
        self.lname = dic["lname"]
        self.email = dic["email"]
