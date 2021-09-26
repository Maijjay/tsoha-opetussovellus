from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
db = SQLAlchemy(app)

app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False



@app.route("/register" ,methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    user_type = request.form["user_type"]

    hash_value = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (username, password, user_type) VALUES (:username, :password, :user_type)"
        db.session.execute(sql, {"username":username, "password":hash_value, "user_type":user_type})
        db.session.commit()
    except IntegrityError:
        print("Username already in use")

    return redirect("/")


@app.route("/login" ,methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    
    print(username, password, "asd")

    sql = "SELECT id, password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        print("Wrong username")
        return redirect("/")
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            print("Username and password correct")
        else:
            print("Wrong password")
            return redirect("/")
    session["username"] = username
    return redirect("/courses")


@app.route("/logout")
def logout():
    print("Loggin out")
    del session["username"]
    return redirect("/")


@app.route("/courses")
def courses():
    print("asd1")

    result = db.session.execute("SELECT coursename FROM courses")
    kurssit = result.fetchall()

    return render_template("courses.html", count=len(courses), courses=courses)

@app.route("/courses/<coursename>", methods=["GET"])
def coursepage(coursename):
    a = "qeeqwe"
    print("course")
    
    return render_template("courses.html")

   
@app.route("/")
def frontpage():
    return render_template("index.html") 

if __name__ == "__main__":
    app.run(debug=True)
