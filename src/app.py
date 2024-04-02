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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userinfo.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 15)
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'User'
    username = db.Column(db.String(20), primary_key = True)
    password = db.Column(db.String(40), nullable=False)
    clas = db.Column(db.String(20), nullable=False)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return redirect(url_for("Home"))

@app.route("/Signup", methods = ["POST", "GET"])
def Signup():
    if request.method=="POST":
        username1 = request.form['username']
        password1 = request.form['password']
    
        rows = db.session.query(User).filter(User.username == username1).count()
        
        if rows==0:
            newuser = User(username = username1, password = password1, clas='Student')
            db.session.add(newuser)
            db.session.commit()
            return redirect(url_for("login"))
        else:
            flash("The username already exists")
    return render_template("Signup.html")

@app.route("/Login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
    
        rows = db.session.query(User).filter(User.username == username and User.password==password).count()
        if rows==0:
             flash("The username and/or password is invalid")
        else:
            session["user"] = username
            return redirect(url_for("Home"))
    return render_template("Login.html")
    
@app.route("/Assignment")
def assignment():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("Assignment.html")

@app.route("/Calendar")
def Calendar():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("Calendar.html")  

@app.route("/Contact")
def Contact():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("Contact.html")

@app.route("/Home")
def Home():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/Labs")
def Labs():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("Labs.html")

@app.route("/Lectures")
def Lectures():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("Lectures.html")

@app.route("/Resources")
def Resources():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("Resources.html")

@app.route("/Tests")
def Tests():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("Tests.html")

if __name__=="__main__":
    app.secret_key = b"secretkey"
    app.run(debug=True)