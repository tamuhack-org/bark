from __future__ import print_function  # In python 2.7
from flask import Flask, render_template, request, redirect, url_for
from resources import pymongo_interface
from flask_pymongo import PyMongo
import os
import sys
import json
import re
from bson.objectid import ObjectId

"""
TODO:
1) csv upload
    - for every input entry, make a key/value and don't duplicate on email
2) make an internal save and a save method
3) add a part of the app to add travel reimbursement amount
4) modal?
"""

app = Flask(__name__)

# testing locally
app.config['MONGO_DBNAME'] = 'bellbird'
mongo = PyMongo(app)
database = pymongo_interface.PyMongoHandler(mongo)


@app.route('/')
def home_page():
    count = database.count()
    return render_template('home.html', count=count)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    person_id = request.args.get('id', None)
    if person_id:
        unique_person = database.get_applicant({"_id": ObjectId(person_id)})
        return render_template('profile.html', entry=unique_person)
    return redirect(url_for("participants", msg="A specific person wasn't requested"))


@app.route('/profile/check-in', methods=['GET'])
def check_in():
    print ("oh boy its kinda working!")
    action = request.args.get('action', "")
    if action == "true":
        msg = "i'm gonna check this dude in"
        print (msg)
    else:
        msg = "hasn't showed up yet"
    return redirect(url_for('participants', msg=msg))


@app.route("/add-delete", methods=['GET', 'POST'])
def modify():
    if request.method == 'POST':
        if request.form['action'] == 'add':
            num_uploads, num_repeats = 0, 0
            first_name, last_name, email = request.form[
                'fname_add'], request.form['lname_add'], request.form['email_add']
            if first_name and last_name and email:
                save_dict = {"first_name": first_name,
                             "last_name": last_name, "email": email}
                saved_data = database.save([save_dict])
                num_uploads, num_repeats = saved_data["uploads"], saved_data["repeats"]
            output_str = "Successfully Uploaded " + \
                str(num_uploads) + " document(s) with " + \
                str(num_repeats) + " repeat(s)"
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
    re_q = re.compile(query_string, re.IGNORECASE)
    query_phrase = {"$or": [{"first_name": re_q},
                            {"last_name": re_q},
                            {"email": re_q}]}
    if not query:
        query_phrase = {}
    page_result = database.get_paginated_entries(
        page_num=page, query_phrase=query_phrase)
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
