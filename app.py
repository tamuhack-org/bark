from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine, QuerySet
from mongoengine.queryset.visitor import Q
from resources import typeform, mongo_interface
import os

CONFIG_VALUES = {"28125773": "first_name", "28125775": "last_name",
                        "28125781": "gender", "28127706": "travel",
                        "28127225": "additional", "28125780": "experience",
                        "28127904": "major", "28125779": "email",
                        "28141455": "race", "28125778": "number",
                        "28128125": "school", "28158536": "resume"}

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'm_engine_db',
    'host': 'mongodb://tamuhack17:Tamuhackdb17@ds129600.mlab.com:29600/m_engine_db'
}

# things that need to be added
#   1: write a "delete" method that considers elements that don't exist
#   2: pagination on results page
#   3: Back buttons on all pages to get back home?
#   4: loading html div for upload pages

mongo_interface.db.init_app(app)
Person = mongo_interface.Person
# the parser takes data from the json requests
parser = typeform.Typeform_Parser(CONFIG_VALUES)
# db_handler class does all of the saving and deleting in our mongo instance
db_handler = mongo_interface.DB_Handler(Person, CONFIG_VALUES)


@app.route('/')
def home_page():
    # we can get info from a mongo document
    count = Person.objects.count()
    return render_template('home.html', count=count)


# route that handles buttons on the home page
@app.route("/modify", methods=['GET', 'POST'])
def modify():
    people = Person.objects()
    if request.method == 'POST':
        # adding a new member
        entries = get_paginated_entries(people, page=1)
        if request.form['action'] == 'add':
            num_uploads, num_repeats = 0, 0
            first_name = request.form['fname_add']
            last_name = request.form['lname_add']
            email = request.form['email_add']
            # if all the blanks are full, reassign above variables and perform a save operation
            if first_name and last_name and email:
                save_dict = {"first_name": first_name, "last_name": last_name, "email": email}
                saved_data = db_handler.save_single(save_dict)
                num_uploads, num_repeats = saved_data["uploads"], saved_data["repeats"]
            # generation an output string when a post request is performed
            output_str = "Successfully Uploaded " + str(num_uploads) + " document(s) with " + str(
                num_repeats) + " repeat(s)"
            return render_template('results.html', count=people.count(), entries=entries, msg=output_str)
        # deleting a member given his/her email
        elif request.form['action'] == 'delete':
            query = request.form['email_delete']
            num_delete = db_handler.delete_single(query)["deleted"]
            output_str = "Successfully Deleted " + str(num_delete)
            return render_template('results.html', count=people.count(), entries=entries, msg=output_str)
    elif request.method == 'GET':
        return render_template('add_delete.html', count=people.count())


@app.route('/upload')
def upload():
    count = Person.objects.count()
    entries = get_paginated_entries(Person.objects(), page=1)
    action = request.args.get('action', '')
    if action == 'uploaded':
        saved_data = db_handler.save_group(parser.parse_data())
        num_uploads, num_repeats = saved_data["uploads"], saved_data["repeats"]
        count = Person.objects.count()
        output_str = "Successfully Uploaded " + str(num_uploads) + " document(s) with " + str(
            num_repeats) + " repeat(s)"
        return render_template('results.html', count=count, entries=entries, msg=output_str)
    elif action == 'return':
        return render_template('results.html', count=count, entries=entries, msg="No Upload")


# TODO @himank should this be put onto a person's route?
# route for accepting/rejecting an applicant
# if the person already has a status (rejected or accepted), we return 'reviewed-profile.html' (just an edit button)
# otherwise, return 'profile.html'
@app.route("/status-update", methods=['GET', 'POST'])
def status_update():
    if request.method == 'POST':
        action = request.form['action']
        email = request.form['email']
        if email:
            Person.objects(email=email).update_one(set__status=action)
    return redirect(url_for('participants'))


@app.route('/participants')
def participants():
    """
    Endpoint to display list of participants
    :return: 
    """
    # if the something is sent via the action argument (happens only with an upload)
    # reload the page for blank page number i.e. page=''
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        return redirect(url_for('participants'))

    count = Person.objects.count()
    entries = get_paginated_entries(Person.objects(), page=page)
    query = request.args.get('q')

    # reload the page for blank query
    if query == '':
        return redirect(url_for('participants'))

    if query:
        entries = get_paginated_entries(Person.objects(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
            | Q(email__icontains=query) | Q(status__exact=query)), page)
    context = dict(
        count=count,
        entries=entries,
        query=query,
        msg="Displaying Search Results"
    )
    return render_template('results.html', **context)


def get_paginated_entries(entries, page):
    """
    Returns paginated entries. Used for participants endpoint.
    :param entries: list of entries
    :param page: current page number
    :return: paginated entries
    """
    return entries.paginate(page=page, per_page=10)


@app.route("/confirm", methods=['GET', 'POST'])
def confirm():
    if request.method == 'GET':
        # loads data into the parser
        count = Person.objects.count()
        data = parser.parse_preview()
        preview = data["data"]
        new_count = data["count"]
        return render_template('confirm.html', count=count, sample_data=preview, count_diff=new_count,
                               msg="For uploading data from a request")


# if the person hasn't been reviewed or the get request has a special "edit" tag, we let them edit
@app.route('/profile/<person_id>')
def profile(person_id):
    action = request.args.get('action', '')
    # if a next tag is attached to the request, find a document that hasn't been reviewed yet
    unique_person = Person.objects.get(id=person_id)
    if action == 'next':
        other_entries = Person.objects(status="not-reviewed", id__ne=person_id)
        # if a person that hasn't been reviewed exists, overwrite "unique person"
        if other_entries:
            unique_person = other_entries[0]
        else:
            return render_template('results.html', count=Person.objects.count(),
                                   entries=Person.objects(), msg="All applicants have been reviewed")
    #if there's an edit tag, who all options
    elif action == "edit":
        return render_template('profile.html', entry=unique_person)
    # otherwise, render a template that requires to click 'edit'
    return render_template('reviewed-profile.html', entry=unique_person)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
