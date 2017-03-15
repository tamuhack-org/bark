from mongoengine import *

    first_name = StringField(required = True)
    last_name = StringField(required = True)
    def save_current(self):
        self.save()
