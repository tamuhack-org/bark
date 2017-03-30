import flask_mongoengine

db = flask_mongoengine.MongoEngine()


#creating a simple Person Class
class Person(db.DynamicDocument):
    #note: it looks like a dynamic field requires a "require" attribute
    email = db.StringField(required=True)

def say_shit():
    print "hello"
#Note: method below has been moved to "typeform.py"
#
# def save_update(data_list):
#     for person_data in data_list:
#         try:
#             #if the person object exists with a given email, ignore it
#             Person.objects.get(email=person_data["email"])
#             print person_data["email"]
#         except Exception:
#             #if we get a "does not exist", create a new person
#             p = Person()
#             for x in person_data:
#                 setattr(p, x, person_data[x])
#             p.save()
