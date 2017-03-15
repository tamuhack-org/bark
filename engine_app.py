#from resources import person, parser
from flask import Flask, render_template, request, redirect
from werkzeug import secure_filename
from flask_mongoengine import MongoEngine, QuerySet
from mongoengine.queryset.visitor import Q

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MONGODB_SETTINGS'] = {
    'db': 'm_engine_db',
    'host': 'mongodb://tamuhack17:Tamuhackdb17@ds129600.mlab.com:29600/m_engine_db'
}
db = MongoEngine()
db.init_app(app)

#creating a simple Person Class
class Person(db.DynamicDocument):
    first_name = db.StringField(required = True)
    last_name = db.StringField(required = True)


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
            #email = request.form['email_add']
            if fname and lname:
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
    query = request.args.get('q', '')
    if query:
        entries = Person.objects(Q(first_name__icontains=query)|Q(last_name__icontains=query))
    return render_template('results.html', count=count, entries=entries, query=query)

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        count = Person.objects.count()
        return render_template('upload.html', count=count)
    if request.method == 'POST':
        #when we receive a post reqeust, we need to take the text, convert them to python objects and add these as mm_document
        #note: if there happens to be a repeat, we must consider this and simply overwrite the new information, not a add new
        #cfile = request.files['file']
        #cfile.save(secure_filename(cfile.filename))
        #count = Person.objects.count()
        # pars = parser.Parser(request.form['schema'])
        # print request.form['csv'].splitlines()
        return render_template('upload.html', count=count)


if __name__ == "__main__":
    app.run()
