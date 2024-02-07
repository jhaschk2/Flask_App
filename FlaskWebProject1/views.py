from flask import Flask, make_response, render_template, request
from FlaskWebProject1 import app
from email.feedparser import FeedParser
from urllib.parse import urljoin
from flask_sqlalchemy import SQLAlchemy
from feedwerk import atom
from datetime import datetime
import feedparser
import uuid

FEED_URLS = "https://gioele.uber.space/k/fdla2023/feed1.atom" , "https://fdla-event-manager.fly.dev/feed" , "https://fdla-atom-feed.xyz/feed" , "https://fdla-backend-project.onrender.com/"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def ParseAllFeeds():
    for FEED_URL in FEED_URLS:
        feed = feedparser.parse(FEED_URL)  # obtains feed from the URL

        # makes a list of the AtomIDs of all Events currently in the database
        existentAtomIDs = [event.atomID for event in Happenings.query.all()]
        isInDb = False

        # Loops over all entries in the feed, checks if they are already in the Database using their AtomID and if not adds them
        for entry in feed.entries:
            isInDb = False

            atomID = entry.get("id")

            for existentID in existentAtomIDs:
                if existentID == atomID:
                    isInDb = True
                    break

            if isInDb == True:
                continue

            name = entry.get("author")
            title = entry.get("title")
            updated = entry.get("updated")
            
            print(len(updated))

            if len(updated) == 24:
                updated = updated[:-5]
            elif len(updated) == 20:
                updated = updated[:-1]

            date = datetime.strptime(updated, '%Y-%m-%dT%H:%M:%S')
            description = entry.get("summary")
            published = entry.get("published")
            
            print(len(published))

            if len(published) == 24:
                published = published[:-5]
            elif len(published) == 20:
                published = published[:-1]

            upload = datetime.strptime(published, '%Y-%m-%dT%H:%M:%S')

            event = Happenings(name, title, date, description, upload, atomID)
            db.session.add(event)
            db.session.commit()
    

class Happenings(db.Model):
    __tablename__ = 'submitted_Events'
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100))
    title = db.Column("title", db.String(100))
    date = db.Column("date", db.DateTime)
    description = db.Column("description", db.String(1000))
    upload = db.Column("upload", db.DateTime)
    atomID = db.Column("atomID", db.String(100))

    def __init__(self, name, title, date, description, upload, atomID):
        self.name = name
        self.title = title
        self.date = date
        self.description = description
        self.upload = upload
        self.atomID = atomID


@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def home():
    ParseAllFeeds()

    # Renders the webpage with the content of the database as text
    return render_template('home.html', values=Happenings.query.all())


@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':

        name = request.form["nm"]
        title = request.form["ttl"]
        date = datetime.strptime(request.form["dt"], '%Y-%m-%dT%H:%M')
        description = request.form["desc"]
        upload = datetime.now()
        newuuid = uuid.uuid4()
        atomID = "urn:uuid:" + str(newuuid)
        print(atomID)

        event = Happenings(name, title, date, description, upload, atomID)
        db.session.add(event)
        db.session.commit()

        return render_template('form.html')

    else:
        return render_template('form.html')


@app.route('/atom.xml/')
def feeds():
    
    values = []

    for event in Happenings.query.all():
            title = event.title
            atomID = event.atomID
            published = datetime.strftime(event.upload, '%Y-%m-%dT%H:%M:%S') + "Z"
            updated = datetime.strftime(event.upload, '%Y-%m-%dT%H:%M:%S') + "Z"
            #date = datetime.strftime(event.date, '%Y-%m-%dT%H:%M:%S') + "Z"
            description = event.description
            name = event.name

            values.append({'title': title, 'id': atomID, 'published': published, 'updated': updated, 'summary': description, 'name': name})

    template = render_template('feed.xml', values = values)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response


with app.app_context():
    db.create_all()