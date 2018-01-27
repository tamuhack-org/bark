from __future__ import print_function  # In python 2.7
from StringIO import StringIO
import os
import re
from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from resources import pymongo_interface, read_csv
from bson.objectid import ObjectId

"""
TODO:
1) csv upload
    - for every input entry, make a key/value and don't duplicate on email
2) make an internal save and a save method 3) add a part of the app to add travel reimbursement amount
4) modal?
"""

app = Flask(__name__)
app.debug = True

# testing locally
app.config['MONGO_URI'] = "mongodb://tamuhack17:Tamuhackdb17@ds113826.mlab.com:13826/tamuhack_app"
app.config['MONGO_DBNAME'] = "tamuhack_app"
mongo = PyMongo(app)

REQUIRED_FIELDS = ["email", "first_name", "last_name"]
ADDITIONAL_FIELDS = ["checked_in", "additional", "travel_reimbursement"]
database = pymongo_interface.PyMongoHandler(
    mongo, REQUIRED_FIELDS, ADDITIONAL_FIELDS)


@app.route('/')
def home_page():
    count = database.count()
    return render_template('home.html', count=count)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    person_id = request.args.get('id', None)
    if person_id:
        unique_person = database.get_applicant_by_id(
            {"_id": ObjectId(person_id)})
        return render_template('profile.html', entry=unique_person)
    return redirect(url_for("participants", msg="A specific person wasn't requested"))


@app.route('/checkin', methods=["GET", "POST"])
def update():
    if request.method == 'POST':
        query = request.form.get('query', "")
        person_id = request.form.get('id')
        action = request.form.get('action', '')
        reimbursement = request.form.get('reimbursement', '')
        additional = request.form.get('additional', '')
        if person_id:
            if action == "checkin":
                database.checkin_applicant(person_id=person_id)
            elif action == "uncheck":
                database.uncheck_applicant(person_id=person_id)
            database.update_applicant_info(
                person_id=person_id, info_str=additional)
            database.update_applicant_reimbursement(
                person_id=person_id, reimbursement_str=reimbursement)
        return redirect(url_for('participants', q=query))
    else:
        person_id = request.args.get('id', "")
        applicant = database.get_applicant_by_id(ObjectId(person_id))
        return render_template('checkin-info.html', id=(person_id), checked_in=applicant["checked_in"])

@app.route("/modify", methods=['GET', 'POST'])
def modify():
    if request.method == 'POST':
        num_uploads, num_repeats = 0, 0
        submit_val = request.form.get("submit", "")
        first_name = request.form.get("fname_add", "")
        last_name = request.form.get("lname_add", "")
        email = request.form.get("email_add", "")
        if first_name and last_name and email and submit_val:
            save_dict = {"first_name": first_name,
                "last_name": last_name, "email": email}
            if submit_val == "add+checkin":
                save_dict["checked_in"] = "true"
            saved_data = database.save([save_dict])
            num_uploads, num_repeats = saved_data["uploads"], saved_data["repeats"]
        output_str = "Successfully Uploaded " + \
            str(num_uploads) + " document(s) with " + \
            str(num_repeats) + " repeat(s)"
        return redirect(url_for('participants', msg=output_str))
    elif request.method == 'GET':
        return render_template('add_delete.html', count=database.count())

def _pagination_ellipsis(currentPage, nrOfPages):
    delta = 2
    t_range = []
    rangeWithDots = []
    t_range.append(1)
    l = None
    if (nrOfPages <= 1):
 	    return t_range
    for i in xrange(currentPage - delta, currentPage + delta+1):
        if (i < nrOfPages and i > 1):
            t_range.append(i)
    t_range.append(nrOfPages)
    for i in t_range:
        if l:
            if (i - l == 2):
                rangeWithDots.append(l + 1)
            elif (i - l != 1):
                rangeWithDots.append('...')
        rangeWithDots.append(i)
        l = i
    return rangeWithDots

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
        pagination_ellipsis = _pagination_ellipsis(page_result["page_num"], page_result["num_pages"]),
        query=query,
        msg=msg,
        count=database.count()
    )
    print (query)
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
            return render_template("upload.html")
    if request.method == 'POST':
        input_file = request.files['data_file']
        if not input_file:
            return "No file"
        io = StringIO(input_file.stream.read())
        csv_handler = read_csv.CsvHandler(
            input_data=io, input_required=REQUIRED_FIELDS)
        database.save(csv_handler.generate_documents())
        return redirect(url_for("participants"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
