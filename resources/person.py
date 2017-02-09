class Person:
    def __init__(self, *initial_data, **kwargs): 
    
    #^ we are gonna wanna use kwargs.
    #^ http://stackoverflow.com/questions/2466191/set-attributes-from-dictionary-in-python 
    #^ if you dont know what im talking about
    
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])
    # once we have a full list of all the attributes finalized we can add 
    # a safeguard that makes sure attributes that werent set are set to None.
    # We honestly dont even have to do that bc we are using NoSQL. But if we 
    # want to standardized all the objects we can. 
    
    def toDict(self):
        #returns a dictionsary with ifnromation for a given person
        # self.dict already does this. (we can delete this function but i left it in to show you)
        return self.__dict__

    def updateAttributes(self, dic):
        # I changed the name bc I thought "fromDict" didnt explain the purpose very well.
        #updates a given person based on an inputted dictionary
        for key in dic:
            setattr(self, key, dic[key]) 
