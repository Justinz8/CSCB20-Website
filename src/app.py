from flask import (Flask,redirect,
    render_template,
    request,
    url_for,
    session,
    abort,
    flash)
import sqlite3
from sqlalchemy import text, desc
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
    
class anonFeedback(db.Model):
    __tablename__='anonFeedback'
    id = db.Column(db.Integer, primary_key=True)
    Feedback = db.Column(db.Text)
    Prof = db.Column(db.Text)
    qnmb = db.Column(db.Integer)
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
    if session["user"]["clas"]!="Student": return redirect(url_for("Home"))
    grades = {}
    
    for i in courseworks:
        q = db.session.query(Notes).filter(Notes.type==i, Notes.user==session["user"]["name"])
        if q.count()==0:
            grades[i]=gradeEntry("Not Submitted", "Not Submitted")
        else:
            q = q.first()
            grades[i]=gradeEntry(q.grade, q.extraNotes)
    
    return render_template("Grades.html", user=session["user"], grades=grades, courseworks=courseworks)

@app.route("/Calendar")
def Calendar():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("Calendar.html", user=session["user"])  

@app.route("/Contact")
def Contact():
    if "user" not in session: return redirect(url_for("login"))
    if session["user"]["clas"]!="Student": return redirect(url_for("Home"))
    
    q = db.session.query(User).with_entities(User.username).filter(User.clas=="Prof.").all()
    
    return render_template("Contact.html", user=session["user"], profs = q)

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

@app.route("/Marks", methods = ["POST", "GET"])
def Marks():
    StudentGrades = None
    if request.method=="POST":
        u = request.form["student"]
        StudentGrades = {}
        for i in courseworks:
            q1 = db.session.query(Notes).filter(Notes.type==i, Notes.user==u)
            if q1.count()==0:
                StudentGrades[i]=gradeEntry("Not Submitted", "Not Submitted")
            else:
                q1 = q1.first()
                StudentGrades[i]=gradeEntry(q1.grade, q1.extraNotes)
        
    if "user" not in session: return redirect(url_for("login"))
    if session["user"]["clas"]!="Prof.": return redirect(url_for("Home"))
    
    q = db.session.query(User).with_entities(User.username).filter(User.clas=="Student").all()
    
    
    return render_template("Marks.html", user=session["user"], users = q, SGrades = StudentGrades, courseworks = courseworks)

@app.route("/Feedback")
def Feedback():
    if "user" not in session: return redirect(url_for("login"))
    if session["user"]["clas"]!="Prof.": return redirect(url_for("Home"))
    
    questions = {}
    
    for i in range(1, 5):
        questions[i] = db.session.query(anonFeedback).with_entities(anonFeedback.Feedback).filter(anonFeedback.Prof==session["user"]["name"], anonFeedback.qnmb==i).all()
    print(questions[1][0])
    return render_template("Feedback.html", user=session["user"], questions = questions)

@app.route("/Logout")
def Logout():
    session.pop("user")
    return redirect(url_for("login"))

@app.route("/SubmitGrade", methods = ["POST", "GET"])
def SubmitGrade():
    if(request.method=="POST"):
        studentName = request.form["student"]
        courseWork = request.form["work"]
        gradePerc = request.form["grade"]
        ExtraNotes = request.form["extraNotes"]
        
        q = db.session.query(Notes).filter(Notes.type==courseWork, Notes.user==studentName)
        if q.count()==0:
            newNote = Notes(type = courseWork, user = studentName, grade = gradePerc, extraNotes=ExtraNotes)
            q.session.add(newNote)
        else:
            q.first().extraNotes=ExtraNotes
            q.first().grade=gradePerc
        q.session.commit()
    return redirect(url_for("Marks"))

@app.route("/SubmitFeedback", methods = ["POST", "GET"])
def SubmitFeedback():
    if(request.method=='POST'):
        q = db.session.query(anonFeedback).order_by(desc(anonFeedback.id))
        idnmb = 0
        if q.count()!=0:
            idnmb = q.first().id+1
        db.session.add(anonFeedback(id=idnmb, Feedback=request.form['q1'], qnmb=1, Prof=request.form['professor']))
        db.session.add(anonFeedback(id=idnmb+1, Feedback=request.form['q2'], qnmb=2, Prof=request.form['professor']))
        db.session.add(anonFeedback(id=idnmb+2, Feedback=request.form['q3'], qnmb=3, Prof=request.form['professor']))
        db.session.add(anonFeedback(id=idnmb+3, Feedback=request.form['q4'], qnmb=4, Prof=request.form['professor']))
        db.session.commit()
    return redirect(url_for("Contact"))

@app.route("/remarkReq", methods=["POST", "GET"])
def remarkReq():
    if(request.method=='POST'):
        work1 = request.form['work']
        reason1 = request.form['reason']
        user1 = session["user"]["name"]
        
        q = db.session.query(Remarks).filter(Remarks.user==user1, Remarks.work==work1)
        
        if q.count()!=0:
            flash("theres already an ongoing remark for this course work")
        else:
            q1 = db.session.query(Notes).filter(Notes.type==work1, Notes.user==user1)
            if q1.count()==0:
                flash("This assignment hasnt been graded yet")
            else:
                db.session.add(Remarks(work=work1, reason=reason1, user=user1))
                db.session.commit()
    
    return redirect(url_for("Grades"))

@app.route("/ReMarks")
def ReMarks():
    if "user" not in session: return redirect(url_for("login"))
    if session["user"]["clas"]!="Prof.": return redirect(url_for("Home"))
    
    q = db.session.query(Remarks).all()
    
    return render_template("Remarks.html", user = session["user"], RemarkCont = q)

@app.route("/SubmitReMarks", methods = ["POST", "GET"])
def SubmitReMarks():
    if request.method=="POST":
        StudentName = request.form["GUser"]
        work = request.form["work"]
        grade = request.form["grade"]
        q = db.session.query(Notes).filter(Notes.user==StudentName, Notes.type==work).first()
        q.grade=grade
        q = db.session.query(Remarks).filter(Remarks.user==StudentName, Remarks.work==work).first()
        db.session.delete(q)
        db.session.commit()
    return redirect(url_for("ReMarks"))

@app.route("/ResolveReMarks", methods= ["POST", "GET"])
def ResolveReMarks():
    if request.method=="POST":
        StudentName = request.form["GUser"]
        work = request.form["work"]
        q = db.session.query(Remarks).filter(Remarks.user==StudentName, Remarks.work==work).first()
        db.session.delete(q)
        db.session.commit()
    return redirect(url_for("ReMarks"))
        

if __name__=="__main__":
    app.run(debug=True)