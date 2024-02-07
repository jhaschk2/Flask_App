from flask import Flask, make_response, redirect, render_template, request, json, url_for, session, flash
from sqlalchemy import true
from FlaskWebProject1 import app
from datetime import datetime
import uuid
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse
import mimetypes

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///actors.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_BINDS']={'two':'sqlite:///events.sqlite3', 'three':'sqlite:///accepted.sqlite3', 'four':'sqlite:///rejected.sqlite3'}

db = SQLAlchemy(app)

class Actors(db.Model):
    __tablename__ = 'Actors'
    _id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column("username", db.String(25))

    def __init__(self, username):
        self.username = username

class Events(db.Model):
    __bind_key__='two'
    __tablename__ = 'Events'
    _id = db.Column("id", db.Integer, primary_key=True)
    eventid = db.Column("eventid", db.String(500))
    name = db.Column("name", db.String(200))
    content = db.Column("description", db.String(500))
    location = db.Column("location", db.String(200))
    startTime = db.Column("startTime", db.String(200))
    endTime = db.Column("endTime", db.String(200))
    published = db.Column("published", db.String(200))
    updated = db.Column("updated", db.String(200))
    attributedTo = db.Column("attributedTo", db.String(500))

    def __init__(self, eventid, name, content, location, startTime, endTime, published, updated, attributedTo):
        self.eventid = eventid
        self.name = name
        self.content = content
        self.location = location
        self.startTime = startTime
        self.endTime = endTime
        self.published = published
        self.updated = updated
        self.attributedTo = attributedTo


class Accepted(db.Model):
    __bind_key__='three'
    __tablename__ = 'Accepted'
    _id = db.Column("id", db.Integer, primary_key=True)
    eventid = db.Column("eventid", db.String(500))
    totalItems = db.Column("totalItems", db.Integer())
    attendees = db.Column("attendees", db.ARRAY(db.String(500)))

    def __init__(self, userid, eventid, totalItems, attendees):
        self.eventid = eventid
        self.totalItems = totalItems
        self.attendees = attendees

class Rejected(db.Model):
    __bind_key__='four'
    __tablename__ = 'Rejected'
    _id = db.Column("id", db.Integer, primary_key=True)
    eventid = db.Column("eventid", db.String(500))
    totalItems = db.Column("totalItems", db.Integer())
    nonattendees = db.Column("nonattendees", db.ARRAY(db.String(500)))

    def __init__(self, eventid, totalItems, nonattendees):
        self.eventid = eventid
        self.totalItems = totalItems
        self.nonattendees = nonattendees

def Accept():
    return

def Reject():
    return

@app.route('/')
@app.route('/start', methods=['GET', 'POST'])
def start():
    session.pop("user", None)
    return render_template('home_alt.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        isInDb = False
        username = request.form["user_name"]
        
        existentUserNames = [actor.username for actor in Actors.query.all()]

        for existentName in existentUserNames:
            if existentName == username:
                flash("Login Successful!")
                isInDb = True
                
        if isInDb == False:
            actor = Actors(username)
            db.session.add(actor)
            db.session.commit()
            flash("New Actor Created!")
                
        session["user"] = username
        
        return redirect (url_for('home', user = username))
    else:
        if "user" in session:
            username = session["user"]
            flash("Already Logged In!")
            return redirect (url_for('home', user = username))
        else:
            return render_template('login.html')


@app.route("/home/<user>")
def home(user):
    if "user" in session:
        user = session["user"]
        return render_template('homepage.html', user=user)
    else:
        return redirect(url_for("login"))


@app.route("/userInbox/<user>")
def userInbox(user):
        return render_template('inbox.html', events=Events.query.all())


@app.route("/inbox")
def inbox():
    if request.method == 'POST':
        request_data = request.get_json()
        
        if request_data["type"] == "Create":
            
            eventid = request_data["object"]["id"]
            name = request_data["object"]["name"]
            content = request_data["object"]["content"]
            location = request_data["object"]["location"]
            startTime = request_data["object"]["startTime"]
            endTime = request_data["object"]["endTime"]
            published = request_data["object"]["published"]
            updated = request_data["object"]["updated"]
            attributedTo = request_data["object"]["attributedTo"]
        
            event = Events(eventid, name, content, location, startTime, endTime, published, updated, attributedTo)
            db.session.add(event)
            db.session.commit()

            return 200
        
        elif request_data["type"] == "Delete":
            
            deleter = request_data["actor"]
            eventID = request_data["object"]["id"]
            
            eventToDelete = Events.query.get_or_404(eventID)
            
            if eventToDelete.attributedTo == deleter:
                db.session.delete(eventToDelete)
                db.session.commit

            return 200
        
        elif request_data["type"] == "Update":
            
            eventID = request_data["object"]["id"]
            
            eventToUpdate = Events.query.get_or_404(eventID)
            
            if request_data["object"]["name"] != None:
                eventToUpdate.name = request_data["object"]["name"]
                
            if request_data["object"]["content"] != None:
                eventToUpdate.content = request_data["object"]["content"]
                
            if request_data["object"]["location"] != None:
                eventToUpdate.location = request_data["object"]["location"]
                
            if request_data["object"]["startTime"] != None:
                eventToUpdate.startTime = request_data["object"]["startTime"]
                
            if request_data["object"]["endTime"] != None:
                eventToUpdate.endTime = request_data["object"]["endTime"]
                
            eventToUpdate.updated = request_data["object"]["updated"]

            db.session.add(eventToUpdate)
            db.session.commit()

            return 200
        
        elif request_data["type"] == "Accept":
            
            acceptedEvent = request_data["object"]["id"]
            accepter = request_data["actor"]
            
            eventToUpdate = Accepted.query.get(acceptedEvent)
            
            if eventToUpdate == None:
                eventID = acceptedEvent
                totalItems = 1
                attendees = [accepter]
                
                accepted = Accepted(eventID, totalItems, attendees)
                db.session.add(accepted)
                db.session.commit()
                
            else:
                eventID = acceptedEvent
                totalItems = eventToUpdate.totalItems + 1
                attendees = eventToUpdate.attendees.append(accepter)

                accepted = Accepted(eventID, totalItems, attendees)
                db.session.add(accepted)
                db.session.commit()

            return 200
        
        elif request_data["type"] == "Reject":
            
            rejectedEvent = request_data["object"]["id"]
            rejecter = request_data["actor"]

            eventToUpdate = Rejected.query.get(rejectedEvent)
            
            if eventToUpdate == None:
                eventID = rejectedEvent
                totalItems = 1
                nonattendees = [rejecter]
                
                rejected = Rejected(eventID, totalItems, nonattendees)
                db.session.add(rejected)
                db.session.commit()
                
            else:
                eventID = rejectedEvent
                totalItems = eventToUpdate.totalItems + 1
                nonattendees = eventToUpdate.nonattendees.append(rejecter)

                accepted = Rejected(eventID, totalItems, nonattendees)
                db.session.add(rejected)
                db.session.commit()

            return 200
        
    else:
        if "user" in session:
            user = session["user"]
            return redirect (url_for('userInbox', user = user))


@app.route("/logout")
def logout():
    if "user" in session:
        user = session["user"]
        flash("You have been logged out!", "info")
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':

        name = request.form["name"]
        content = request.form["content"]
        startTime = request.form["startTime"]
        endTime = request.form["endTime"]
        location = request.form["location"]
        imageLink = request.form["image"]
        imageName = request.form["image_name"]

        output = {}
        
        output["@context"] = "https://www.w3.org/ns/activitystreams"
        output["type"] = "Create"
        output["actor"] = urlparse(request.base_url) + "/" + session["user"]
        output["object"] = {}

        output["object"]["@context"] = "https://www.w3.org/ns/activitystreams" 
        newuuid = uuid.uuid4()
        eventid = urlparse(request.base_url) + "/event/" + str(newuuid)
        output["object"]["id"] = eventid
        output["object"]["type"] = "Event"
        output["object"]["name"] = name
        output["object"]["content"] = content
        output["object"]["location"] = location
        output["object"]["startTime"] = startTime
        output["object"]["endTime"] = endTime
        currentTime = datetime.now()
        output["object"]["published"] = datetime.strftime(currentTime, '%Y-%m-%dT%H:%M:%S')
        output["object"]["updated"] = datetime.strftime(currentTime, '%Y-%m-%dT%H:%M:%S')
        output["object"]["attributedTo"] = request.environ['RAW_URI'] + "/" + session["user"]
        
        output["object"]["image"] = {}
        
        if imageLink != "":
            newuuid = uuid.uuid4()
            imageid = urlparse(request.base_url) + "/image/" + str(newuuid)
        else:
            imageid = ""
        
        output["object"]["image"]["id"] = imageid
        output["object"]["image"]["type"] = "Image"
        output["object"]["image"]["name"] = imageName
        
        if imageLink != "":
            output["object"]["image"]["url"] = []
        
            url = {} 
            url["type"] = "Link"
            url["href"] = imageLink
            url["mediatype"] = mimetypes.guess_type(imageLink)[0]
        
            output["object"]["image"]["url"].append(url)

        output["object"]["accepted"] = {}
        output["object"]["accepted"]["id"] = eventid + "/accepted"
        #output["object"]["accepted"]["summary"] = "Attendees"
        output["object"]["accepted"]["type"] = "Collection"
        #output["object"]["accepted"]["totalItems"] = 0
        #output["object"]["accepted"]["items"] = []
        
        #accepted_items = {}
        #accepted_items["type"] = "Person"
        #accepted_items["id"] = "" 

        #output["object"]["accepted"]["items"].append(accepted_items)
        
        output["object"]["rejected"] = {}
        output["object"]["rejected"]["id"] = eventid + "/rejected"
        #output["object"]["rejected"]["summary"] = "Non-attendees"
        output["object"]["rejected"]["type"] = "Collection"
        #output["object"]["rejected"]["totalItems"] = 0
        #output["object"]["rejected"]["items"] = []
        
        #rejected_items = {}
        #rejected_items["type"] = "Person"
        #rejected_items["id"] = ""

        #output["object"]["rejected"]["items"].append(rejected_items)

        json_object = json.dumps(output, indent=4, sort_keys=False)

        published = output["object"]["published"]
        updated = output["object"]["published"]
        attributedTo = output["actor"]

        event = Events(eventid, name, content, location, startTime, endTime, published, updated, attributedTo)
        db.session.add(event)
        db.session.commit()

        flash("Event submitted!")

        response = request.post("www.app1.com", json=json_object)
        
        if response.status_code == request.codes.ok:
            flash("Send 1 successful!")
        else:
            flash("Send 1 unsuccessful!")

        response = request.post("www.app2.com", json=json_object)
        
        if response.status_code == request.codes.ok:
            flash("Send 2 successful!")
        else:
            flash("Send 2 unsuccessful!")

        return json_object

    else:
        return render_template('form_new.html')

@app.route("/event/<id>")
def event(id):
    return render_template('inbox.html', events=Events.query.all())

@app.route("/event/<id>/accepted")
def accepted(id):
    return render_template('inbox.html', events=Events.query.all())

@app.route("/event/<id>/rejected")
def rejected(id):
    return render_template('inbox.html', events=Events.query.all())

@app.route("/image/<id>")
def image(id):
    return render_template('inbox.html', events=Events.query.all())

with app.app_context():
    db.create_all()