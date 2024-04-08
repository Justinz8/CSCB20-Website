from flask import (Flask,redirect,
    render_template,
    request,
    url_for,
    session,
    flash)
from sqlalchemy import desc
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
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
    worktype = db.Column(db.String(20), primary_key = True)
    username = db.Column(db.String(20), db.ForeignKey('User.username'), nullable = False, primary_key=True)
    grade = db.Column(db.Integer)
    extraNotes = db.Column(db.Text)
    
class Remarks(db.Model):
    __tablename__ = 'Remarks'
    worktype = db.Column(db.String(20), primary_key = True)
    username = db.Column(db.String(20), db.ForeignKey('User.username'), nullable = False, primary_key=True)
    reason = db.Column(db.Text)
    
class anonFeedback(db.Model):
    __tablename__='anonFeedback'
    id = db.Column(db.Integer, primary_key=True)
    feedback = db.Column(db.Text)
    instructor = db.Column(db.Text)
    qnmb = db.Column(db.Integer)
class user:
    def __init__(self, username, clas):
        self.username = username
        self.clas = clas
        
class gradeEntry:
    def __init__(self, grade, notes):
        self.grade=grade
        self.notes=notes

with app.app_context():
    db.create_all()

#Signup System:
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

@app.route("/Logout")
def Logout():
    session.pop("user")
    return redirect(url_for("login"))

#Pages without backend:
@app.route("/Calendar")
def Calendar():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("Calendar.html", user=session["user"])  

@app.route("/CourseWork")
def CourseWork():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("CourseWork.html", user=session["user"])

@app.route("/Home")
def Home():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("index.html", user=session["user"])

@app.route("/")
def index():
    return redirect(url_for("Home"))

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

#Student Functionalities:
@app.route("/Contact")
def Contact():
    if "user" not in session: return redirect(url_for("login"))
    if session["user"]["clas"]!="Student": return redirect(url_for("Home"))
    
    q = db.session.query(User).with_entities(User.username).filter(User.clas=="Instructor").all()
    
    return render_template("Contact.html", user=session["user"], instructors = q)

@app.route("/Grades")
def Grades():
    if "user" not in session: return redirect(url_for("login"))
    if session["user"]["clas"]!="Student": return redirect(url_for("Home"))
    grades = {}
    username = session["user"]["username"]
    
    for i in courseworks:
        q = db.session.query(Notes).filter(Notes.worktype==i, Notes.username==username)
        if q.count()==0:
            grades[i]=gradeEntry("Not Submitted", "Not Submitted")
        else:
            q = q.first()
            grades[i]=gradeEntry(q.grade, q.extraNotes)
    
    return render_template("Grades.html", user=session["user"], grades=grades, courseworks=courseworks)

@app.route("/remarkReq", methods=["POST", "GET"])
def remarkReq():
    if(request.method=='POST'):
        worktype1 = request.form['worktype']
        reason1 = request.form['reason']
        user1 = session["user"]["username"]
        
        q = db.session.query(Remarks).filter(Remarks.username==user1, Remarks.worktype==worktype1)
        
        if q.count()!=0:
            flash("theres already an ongoing remark for this course work")
        else:
            q1 = db.session.query(Notes).filter(Notes.worktype==worktype1, Notes.username==user1)
            if q1.count()==0:
                flash("This assignment hasnt been graded yet")
            else:
                db.session.add(Remarks(worktype=worktype1, reason=reason1, username=user1))
                db.session.commit()
    
    return redirect(url_for("Grades"))

@app.route("/SubmitFeedback", methods = ["POST", "GET"])
def SubmitFeedback():
    if(request.method=='POST'):
        instructor1=request.form['instructor']
        q = db.session.query(anonFeedback).order_by(desc(anonFeedback.id))
        idnmb = 0
        if q.count()!=0:
            idnmb = q.first().id+1
        for i in range(1, 5):
            db.session.add(anonFeedback(id=idnmb+i, feedback=request.form['q'+str(i)], qnmb=i, instructor=instructor1))
        db.session.commit()
    return redirect(url_for("Contact"))

#Instructor Functionalities
@app.route("/Marks", methods = ["POST", "GET"])
def Marks():
    StudentGrades = None
    if request.method=="POST":
        StudentUser = request.form["student"]
        StudentGrades = {}
        for i in courseworks:
            q1 = db.session.query(Notes).filter(Notes.worktype==i, Notes.username==StudentUser)
            if q1.count()==0:
                StudentGrades[i]=gradeEntry("Not Submitted", "Not Submitted")
            else:
                q1 = q1.first()
                StudentGrades[i]=gradeEntry(q1.grade, q1.extraNotes)
        
    if "user" not in session: return redirect(url_for("login"))
    if session["user"]["clas"]!="Instructor": return redirect(url_for("Home"))
    
    q = db.session.query(User).with_entities(User.username).filter(User.clas=="Student").all()
    
    
    return render_template("Marks.html", user=session["user"], users = q, SGrades = StudentGrades, courseworks = courseworks)

@app.route("/SubmitGrade", methods = ["POST", "GET"])
def SubmitGrade():
    if(request.method=="POST"):
        studentName = request.form["student"]
        courseWork = request.form["work"]
        gradePerc = request.form["grade"]
        ExtraNotes = request.form["extraNotes"]
        
        q = db.session.query(Notes).filter(Notes.worktype==courseWork, Notes.username==studentName)
        if q.count()==0:
            newNote = Notes(worktype = courseWork, username = studentName, grade = gradePerc, extraNotes=ExtraNotes)
            q.session.add(newNote)
        else:
            q.first().extraNotes=ExtraNotes
            q.first().grade=gradePerc
        q.session.commit()
    return redirect(url_for("Marks"))

@app.route("/Feedback")
def Feedback():
    if "user" not in session: return redirect(url_for("login"))
    if session["user"]["clas"]!="Instructor": return redirect(url_for("Home"))
    
    questions = {}
    username = session["user"]["username"]
    for i in range(1, 5):
        questions[i] = db.session.query(anonFeedback).with_entities(anonFeedback.feedback).filter(anonFeedback.instructor==username, anonFeedback.qnmb==i).all()
    return render_template("Feedback.html", user=session["user"], questions = questions)

@app.route("/ReMarks")
def ReMarks():
    if "user" not in session: return redirect(url_for("login"))
    if session["user"]["clas"]!="Instructor": return redirect(url_for("Home"))
    
    q = db.session.query(Remarks).all()
    
    return render_template("Remarks.html", user = session["user"], RemarkCont = q)

def deleteRemark(StudentName, worktype):
    q = db.session.query(Remarks).filter(Remarks.username==StudentName, Remarks.worktype==worktype).first()
    db.session.delete(q)
    db.session.commit()

@app.route("/SubmitReMarks", methods = ["POST", "GET"])
def SubmitReMarks():
    if request.method=="POST":
        StudentName = request.form["username"]
        worktype = request.form["worktype"]
        grade = request.form["grade"]
        q = db.session.query(Notes).filter(Notes.username==StudentName, Notes.worktype==worktype).first()
        q.grade=grade
        deleteRemark(StudentName, worktype)
    return redirect(url_for("ReMarks"))

@app.route("/ResolveReMarks", methods= ["POST", "GET"])
def ResolveReMarks():
    if request.method=="POST":
        StudentName = request.form["username"]
        worktype = request.form["worktype"]
        deleteRemark(StudentName, worktype)
    return redirect(url_for("ReMarks"))
        

if __name__=="__main__":
    app.run(debug=True)