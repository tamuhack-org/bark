from flask import Flask, render_template, request, redirect
from flask_mongoengine import MongoEngine, QuerySet
from mongoengine.queryset.visitor import Q
from resources import typeform, m_person

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MONGODB_SETTINGS'] = {
    'db': 'm_engine_db',
    'host': 'mongodb://tamuhack17:Tamuhackdb17@ds129600.mlab.com:29600/m_engine_db'
}

#things that need to be added
#   1: error handling for manual upload of an entry
#   2: pagination on results page
#   3: Back buttons on all pages to get back home?
#   4: loading html div for upload pages


m_person.db.init_app(app)
Person = m_person.Person
parser = typeform.Typeform_Parser(Person)

@app.route('/')
def home_page():
    # we can get info from a mongo document
    count = Person.objects.count()
    return render_template('home.html', count = count)


# route that handles buttons on the home page
@app.route("/modify", methods=['GET', 'POST'])
def modify():
    if request.method == 'POST':
        if request.form['action'] == 'add':
            fname = request.form['fname_add']
            lname = request.form['lname_add']
            email = request.form['email_add']
            if fname and lname and email:
                add = Person()
                add.first_name = fname
                add.last_name = lname
                add.save()
            count = Person.objects.count()
            return render_template('add_delete.html', count=count)
        elif request.form['action'] == 'delete':
            query = request.form['fname_delete']
            to_delete = Person.objects(first_name = query)
            to_delete.delete()
            count = Person.objects.count()
            return render_template('add_delete.html', count=count)
    elif request.method == 'GET':
        count = Person.objects.count()
        return render_template('add_delete.html', count=count)

@app.route('/participants')
def participants():
    count = Person.objects.count()
    entries = Person.objects()
    #if the something is sent via the action argument (happens only with an upload)
    action = request.args.get('action', '')
    if action:
        if action == 'uploaded':
            parser.save_data()
            # m_person.save_update(parser.get_data())
            count = Person.objects.count()
            entries = Person.objects()
            return render_template('results.html', count=count, entries=entries, msg = "Successful Upload")
        elif action == 'return':
            return render_template('results.html', count=count, entries=entries, msg = "You didn't upload")
    #otherwise, its a query or an empty query
    else:
        #second value is a default argument ''
        query = request.args.get('q', '')
        if query:
            entries = Person.objects(Q(first_name__icontains=query)|Q(last_name__icontains=query)|Q(email__icontains=query))
        return render_template('results.html', count=count, entries=entries, query=query, msg = "randomshit")

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        #loads data into the parser
        count = Person.objects.count()
        sample = str(parser.get_preview())
        print sample
        count_diff = parser.get_entry_count()
        return render_template('upload.html', count=count, sample_data=sample ,count_diff=count_diff, msg="For uploading data from a request")

if __name__ == "__main__":
    app.run()
