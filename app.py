from __future__ import print_function # In python 2.7
from flask import Flask, render_template, request, redirect, url_for
from resources import typeform, pymongo_interface
from flask_pymongo import PyMongo
import os, sys, json
from bson.objectid import ObjectId

"""
TODO:
-add config file formatting
-refactor the adding method

"""

TYPEFORM_MAPPING = {"63162760" : "first_name", "63162761": "last_name",
                    "63162763": "gender", "63162770": "email",
                    "63162762": "phone", "63162771": "school",
                    "63162765": "major", "63162764": "year",
                    "63162772": "resume", "63162766": "transport",
                    "63162767": "experience", "63162768": "shirt_size",
                    "63162769": "race", "63162773": "personal-links",
                    "custom": "status"
                    }

REQUEST_STRING = "https://api.typeform.com/v1/form/PfNHtQ?key=598bae62949ccf0f2098d86db19592d0aa0a2260"

app = Flask(__name__)

# testing locally
# app.config['MONGO_DBNAME'] = 'bellbird'

# for current participants
app.config['MONGO_URI'] = "mongodb://tamuhack17:Tamuhackdb17@ds113826.mlab.com:13826/tamuhack_app"
app.config['MONGO_DBNAME'] = "tamuhack_app"

# last year's dataset
# app.config['MONGO_URI'] = "mongodb://tamuhack17:Tamuhackdb17@ds129600.mlab.com:29600/m_engine_db"
# app.config['MONGO_DBNAME'] = "m_engine_db"

parser = typeform.Typeform_Parser(values=[v for k,v in TYPEFORM_MAPPING.iteritems()],typeform_mapping=TYPEFORM_MAPPING, request_str=REQUEST_STRING)
mongo = PyMongo(app)
database = pymongo_interface.PyMongoHandler(mongo, TYPEFORM_MAPPING)

@app.route('/')
def home_page():
    count = database.count()
    return render_template('home.html', count=count)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'GET':
        person_id = request.args.get('id', None)
        if person_id:
            unique_person = database.get_applicant({"_id": ObjectId(person_id)}) 
            return render_template('profile.html', entry=unique_person)
        else:
            unique_person = database.get_applicant({"status":""}) 
            if not unique_person:
                params = {"msg": "All applicants have been reviewed!"}
                return redirect(url_for("participants", **params))
            return render_template('profile.html', entry=unique_person)
    if request.method == 'POST':
        action = request.form.get('action', None)
        person_id = request.form.get('id', None)
        if action == "accept" and person_id:
            database.accept_applicant(person_id)
        elif action == "reject" and person_id:
            database.reject_applicant(person_id)
        elif action == "un-reviewed" and person_id:
            database.clear_applicant_status(person_id)
        else:
            params = {"msg": "Incorrect parameters on profile route"}
            return redirect(url_for('participants'), **params)
        return redirect(url_for('profile'))

@app.route("/add-delete", methods=['GET', 'POST'])
def modify():
    if request.method == 'POST':
        if request.form['action'] == 'add':
            num_uploads, num_repeats = 0, 0
            first_name, last_name, email = request.form['fname_add'], request.form['lname_add'], request.form['email_add']
            if first_name and last_name and email:
                save_dict = {"first_name": first_name, "last_name": last_name, "email": email}
                saved_data = database.save([save_dict])
                num_uploads, num_repeats = saved_data["uploads"], saved_data["repeats"]
            output_str = "Successfully Uploaded " + str(num_uploads) + " document(s) with " + str(num_repeats) + " repeat(s)"
        elif request.form['action'] == 'delete':
            query = request.form['email_delete']
            result = database.delete({"email": query}, single=True)
            output_str = "Successfully Deleted " + str(result["deleted"])
        return redirect(url_for('participants', msg=output_str))
    elif request.method == 'GET':
        return render_template('add_delete.html', count=database.count())

@app.route('/participants')
def participants():
    page = int(request.args.get('page', 1))
    msg = request.args.get('msg', "Displaying Search Results")
    query = request.args.get('q', "")
    query_string = ".*" + query + ".*"
    query_phrase = {"$or":[ {"first_name" : {"$regex" : query_string}}, {"last_name" : {"$regex" : query_string}}, {"email" : {"$regex" : query_string}}]}
    if not query: query_phrase = {}
    page_result = database.get_paginated_entries(page_num=page, query_phrase=query_phrase)
    context = dict(
        entries=page_result["entries"],
        num_pages=page_result["num_pages"],
        page_num=page_result["page_num"],
        query=query,
        msg=msg,
        count=database.count()
    )
    return render_template('results.html', **context)

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        action = request.args.get('action', None)
        if action == 'upload_data':
            saved_data = database.save(parser.parse_data())
            num_uploads, num_repeats = saved_data["uploads"], saved_data["repeats"]
            output_str = "Successfully Uploaded " + str(num_uploads) + " document(s) with " + str(
                num_repeats) + " repeat(s)"
            params = {"msg": output_str}
            return redirect(url_for("participants", **params))
        elif action == 'return':
            return redirect(url_for('participants'))
        else:
            count = database.count()
            data = parser.parse_preview()
            preview = data["data"]
            new_count = data["count"]
            return render_template('upload.html', count=count, sample_data=preview, count_diff=new_count,
                            msg="For uploading data from a request")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
