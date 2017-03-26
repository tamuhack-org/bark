#single underscore is a private variable
#double underscore is a "hella" private variable that you should never override/touch

class Person:
    def __init__(self, *initial_data, **kwargs): 
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])
    def toDict(self):
        #returns a dictionsary with ifnromation for a given person
        # self.dict already does this. (we can delete this function but i left it in to show you)
        return self.__dict__
