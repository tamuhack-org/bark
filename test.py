from person import Person
from flask import Flask
from flask_pymongo import PyMongo
from pymongo import MongoClient

#note: in flask-pymongo, the name of this file must be the same name as the databse at hand, in this case, test.

"""
note: in mongo, a document is a an object or a row, and a collection is a table
a column represents a key in the databse and values are analgous
"""
app = Flask(__name__) 
mongo = PyMongo(app)

@app.route('/')
def home_page():
    return str(mongo.db.sites.find_one_or_404({}))

if __name__ == "__main__":
    app.run()

