from flask import (Flask,redirect,
    render_template,
    request,
    url_for,
    session,
    abort,
    flash)
import sqlite3
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt

courseworks = ("Midterm", "Final", "Assignment 1", "Assignment 2", "Assignment 3",
               "Lab 1", "Lab 2", "Lab 3", "Lab 4", "Lab 5", "Lab 6", "Lab 7", "Lab 8",
               "Lab 9", "Lab 10", "Lab 11")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userinfo.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 15)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
class User(db.Model):
    __tablename__ = 'User'
    username = db.Column(db.String(20), primary_key = True)
    password = db.Column(db.String(40), nullable=False)
    clas = db.Column(db.String(20), nullable=False)
    
class Notes(db.Model):
    __tablename__ = 'Notes'
    type = db.Column(db.String(20), primary_key = True)
    user = db.Column(db.String(20), db.ForeignKey('User.username'), nullable = False, primary_key=True)
    grade = db.Column(db.Integer)
    extraNotes = db.Column(db.Text)
    
class Remarks(db.Model):
    __tablename__ = 'Remarks'
    work = db.Column(db.String(20), primary_key = True)
    user = db.Column(db.String(20), db.ForeignKey('User.username'), nullable = False, primary_key=True)
    reason = db.Column(db.Text)
class user:
    def __init__(self, name, clas):
        self.name = name
        self.clas = clas
    
class gradeEntry:
    def __init__(self, grade, notes):
        self.grade=grade
        self.notes=notes

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return redirect(url_for("Home"))

@app.route("/Signup", methods = ["POST", "GET"])
def Signup():
    if "user" in session: return redirect(url_for("Home"))
    if request.method=="POST":
        username1 = request.form['username']
        password1 = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        clas1 = request.form['clas']
    
        rows = db.session.query(User).filter(User.username == username1).count()
        
        if rows==0:
            newuser = User(username = username1, password = password1, clas=clas1)
            db.session.add(newuser)
            db.session.commit()
            return redirect(url_for("login"))
        else:
            flash("The username already exists")
    return render_template("Signup.html", notlogged=True)

@app.route("/Login", methods=["POST", "GET"])
def login():
    if "user" in session: return redirect(url_for("Home"))
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
    
        rows = db.session.query(User).filter(User.username == username).first()
        if not rows or not bcrypt.check_password_hash(rows.password, password):
             flash("The username and/or password is invalid")
        else:
            session["user"] = user(rows.username, rows.clas).__dict__
            return redirect(url_for("Home"))
    return render_template("Login.html", notlogged=True)
    
@app.route("/CourseWork")
def CourseWork():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("CourseWork.html", user=session["user"])

@app.route("/Grades")
def Grades():
    if "user" not in session: return redirect(url_for("login"))
    grades = {}
    
    for i in courseworks:
        q = db.session.query(Notes).filter(Notes.type==i, Notes.user==session["user"]["name"])
        if q.count()==0:
            grades[i]=gradeEntry("Not Submitted", "Not Submitted")
        else:
            q = q.first()
            grades[i]=gradeEntry(q.grade, q.extraNotes)
    
    return render_template("Grades.html", user=session["user"], grades=grades)

@app.route("/Calendar")
def Calendar():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("Calendar.html", user=session["user"])  

@app.route("/Contact")
def Contact():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("Contact.html", user=session["user"])

@app.route("/Home")
def Home():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("index.html", user=session["user"])

@app.route("/Labs")
def Labs():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("Labs.html", user=session["user"])

@app.route("/Lectures")
def Lectures():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("Lectures.html", user=session["user"])

@app.route("/Resources")
def Resources():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("Resources.html", user=session["user"])

@app.route("/Logout")
def Logout():
    session.pop("user")
    return redirect(url_for("login"))

@app.route("/remarkReq", methods=["POST", "GET"])
def remarkReq():
    if(request.method=='POST'):
        work1 = request.form['work']
        reason1 = request.form['reason']
        user1 = session["user"]["name"]
        
        q = db.session.query(Remarks).filter(Remarks.user==user1, Remarks.work==work1)
        print(q.first(), user1, work1)
        if q.count()!=0:
            flash("theres already an ongoing remark for this course work")
        else:
            db.session.add(Remarks(work=work1, reason=reason1, user=user1))
            db.session.commit()
    
    return redirect(url_for("Grades"))

if __name__=="__main__":
    app.run(debug=True)