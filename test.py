from resources import person
from flask import Flask, render_template, request, redirect
from flask_pymongo import PyMongo
from pymongo import MongoClient


"""
note: in mongo, a document is a an object or a row, and a collection is a table
a column represents a key in the databse and values are analgous

note: in flask-pymongo, the name of this file must be the same name as the databse at hand, in this case, test.
"""

#creating a person instance 
b = person.Person() 
app = Flask(__name__) 
mongo = PyMongo(app)

@app.route('/')
def home_page():
    #we can get info from a mongo document
    print str(mongo.db.sites.find_one({}))
    count = mongo.db.sites.count({})
    return render_template('render.html', count=count)

#testing a post method from the form called "render.html" (this is still in progress)
@app.route("/add", methods=['POST'])
def add():
    fname = request.form['fname_add']
    lname = request.form['lname_add']
    email = request.form['email_add']
    mongo.db.sites.insert({"first_name": fname, "last_name": lname, "email": email})
    count = mongo.db.sites.count({})
    return render_template('render.html', count=count)

@app.route('/delete', methods=['POST'])
def delete():
    b = request.form['fname_delete']
    mongo.db.sites.delete_one({"first_name": b})
    count = mongo.db.sites.count({})
    return render_template('render.html', count=count)
            
if __name__ == "__main__":
    app.run()

