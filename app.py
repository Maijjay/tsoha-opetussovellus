from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

db = SQLAlchemy(app)

app.secret_key = getenv("SECRET_KEY") 

# Fix db sql alchemy not accepting postgres://
db_uri = getenv("DATABASE_URL")
if db_uri.startswith("postgres://"):
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
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
    
    print(app.config)
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
    user_type = get_user_type(username)

    print(user_type)

    if user_type == 'opiskelija':
        return redirect("/courses")
    elif user_type == 'opettaja':
        return redirect("/teachercourses")

@app.route("/logout")
def logout():
    print("Loggin out")
    del session["username"]
    return redirect("/")

@app.route("/teachercourses")
def teachercourses():

    username = session["username"]
    user_type = get_user_type(username)
    if user_type == 'opiskelija':
        return redirect("/courses")

    result = db.session.execute("SELECT coursename FROM courses")
    courses = result.fetchall()

    userid = get_user_id(username)

    sql = "SELECT id, coursename FROM courses, users_courses WHERE courses.id = users_courses.courses_id AND users_courses.users_id=:userid"
    result = db.session.execute(sql, {"userid":userid})
    courselist = result.fetchall()

    return render_template("teachercourses.html", count=len(courselist), courselist = courselist)

@app.route("/participants", methods=["POST"])
def participants():
    coursename = request.form["coursename"]
    courses_id = request.form["courses_id"]

    sql = "SELECT users_id FROM users_courses WHERE courses_id = :courses_id"
    result = db.session.execute(sql, {"courses_id":courses_id})
    all_users_id = result.fetchall()
    
    user_exercise_list = []

    for i in range(0, len(all_users_id)):
        userid = all_users_id[i]
        userid =userid[0]

        user_type = "opiskelija"

        sql = "SELECT username FROM users WHERE id = :userid AND user_type = :user_type"
        result = db.session.execute(sql, {"userid":userid, "user_type":user_type})
        username = result.fetchone()
        

        sql = "SELECT finished FROM users_exercises WHERE users_id = :userid AND courses_id = :courses_id"
        result = db.session.execute(sql, {"userid":userid, "courses_id":courses_id})
        done_exercises = result.fetchall()
        done_exercises = len(done_exercises)


        sql = "SELECT id FROM exercises WHERE courses_id = :courses_id"
        result = db.session.execute(sql, {"courses_id":courses_id})
        all_exercises = result.fetchall()

        if username is not None:
            username = username[0]
            user_exercise_list.append([username, done_exercises])

        print(all_exercises)
        print(user_exercise_list)
    return render_template("participants.html", coursename=coursename, user_exercise_list=user_exercise_list, all_exercises=len(all_exercises))

@app.route("/courses")
def courses():

    username = session["username"]
    user_type = get_user_type(username)
    if user_type == 'opettaja':
        return redirect("/teachercourses")

    result = db.session.execute("SELECT coursename FROM courses")
    courses = result.fetchall()

    userid = get_user_id(username)
    
    sql = "SELECT coursename FROM courses, users_courses WHERE courses.id = users_courses.courses_id AND users_courses.users_id=:userid"
    result = db.session.execute(sql, {"userid":userid})
    joined = result.fetchall()

    return render_template("courses.html", count=len(courses), courses=courses, joined_count=len(joined), joined=joined)

@app.route("/courses/<coursename>", methods=["GET"])
def coursepage(coursename):

    sql = "SELECT theory, id FROM courses WHERE coursename = :coursename"
    result = db.session.execute(sql, {"coursename":coursename})
    theory, courses_id = result.fetchone() 
    theorylines = theory.split("\n")

    username = session["username"]
    user_id = get_user_id(username)

    print("TÄSSÄÄÄÄ")
    exercises = []
    done_exercises = 0
    try:
        sql = "SELECT id FROM exercises WHERE courses_id = :courses_id"
        result = db.session.execute(sql, {"courses_id":courses_id})
        allexercises = result.fetchall()

        if (len(allexercises) > 0):
            exercises_id = []
            for i in range(0, len(allexercises)):
                exid = allexercises[i]
                exid=exid[0] 
                print("TÄSSÄÄÄÄ")
                no = False
                sql = "SELECT exercises_id FROM users_exercises WHERE users_id = :user_id AND exercises_id = :exid AND finished = :no"
                result = db.session.execute(sql, {"user_id":user_id, "exid":exid, "no":no})
                exid = result.fetchone()
                
                if exid is not None:
                    exercises_id.append(exid)
                    print(exercises)
            done_exercises = len(allexercises) - len(exercises_id)
            print("TÄSSÄÄÄÄ")
            for i in range(0, len(exercises_id)):
                exid = exercises_id[i]
                exid=exid[0]

                sql = "SELECT assignment FROM exercises WHERE id = :exid"
                result = db.session.execute(sql, {"exid":exid})
                assignment = result.fetchone().assignment
                print("TÄSSÄÄÄÄ")
                choises = [] 
                sql = "SELECT choice FROM choices WHERE exercises_id = :exid"
                result = db.session.execute(sql, {"exid":exid})
                choices = result.fetchall()
                
                for j in range(0, len(choices)):
                    choices[j] = choices[j][0]
                print("TÄSSÄÄÄÄ")
                exercises.append([exid, assignment, choices])
                print("ONNISTUI")
    except AttributeError:
        print("EI ONNISTU")
        return render_template("course.html", coursename=coursename, theorylines=theorylines)         
    print("TÄSSÄÄÄÄ")
    return render_template("course.html", coursename=coursename, theorylines=theorylines, exercises=exercises, exercises_count=len(allexercises), done_exercises=done_exercises)

@app.route("/answer", methods=["POST"])
def answer():
    answer = request.form["answer"]
    exercises_id = request.form["exercises_id"]
    coursename = request.form["coursename"]

    try:
        sql = "SELECT id FROM answers WHERE answer=:answer AND exercises_id=:exercises_id"
        result = db.session.execute(sql, {"answer":answer, "exercises_id":exercises_id })
        answerid = result.fetchone().id

        course_id = get_course_id(coursename)

        username = session["username"]
        user_id = get_user_id(username)

        sql = "UPDATE users_exercises SET finished = TRUE WHERE users_id = :user_id AND courses_id = :course_id AND exercises_id = :exercises_id"
        db.session.execute(sql, {"user_id":user_id, "course_id":course_id, "exercises_id":exercises_id})
        db.session.commit() 

        print("PÄIVITETTY listalle")
    except AttributeError:
        print("Wrong answer")

    return redirect("/courses/" + coursename)

@app.route("/join_course", methods=["POST"])
def join_course():

    username = session["username"]
    userid = get_user_id(username)
    
    coursename = request.form["coursename"]
    courseid = get_course_id(coursename)

    sql = "SELECT users_id, courses_id FROM users_courses WHERE (users_id = :userid AND courses_id = :courseid)"
    result = db.session.execute(sql, {"userid":userid, "courseid":courseid})
    joined = result.fetchone()

    if not joined:
        sql = "INSERT INTO users_courses (users_id, courses_id) VALUES (:userid, :courseid)"
        db.session.execute(sql, {"userid":userid, "courseid":courseid})

        sql = "SELECT id FROM exercises WHERE courses_id=:courseid"
        result = db.session.execute(sql, {"courseid":courseid})
        exerciseid = result.fetchall()

        for ex in exerciseid:
            ex = ex[0]
            if ex != "":
                finished = False
                sql = "INSERT INTO users_exercises (users_id, courses_id, exercises_id, finished) VALUES (:userid, :courseid, :ex, :finished)"
                db.session.execute(sql, {"userid":userid, "courseid":courseid, "ex":ex, "finished":finished})
        db.session.commit()

    return redirect("/courses")

@app.route("/leave_course", methods=["POST"])
def leave_course():

    username = session["username"]
    users_id = get_user_id(username)

    coursename = request.form["coursename"]
    courses_id = get_course_id(coursename)

    sql = "DELETE FROM users_courses WHERE courses_id = :courses_id AND users_id = :users_id"
    result = db.session.execute(sql, {"courses_id":courses_id, "users_id":users_id})
    db.session.commit()

    return redirect("/courses")

@app.route("/newcourse")
def newcourse():
    return render_template("newcourse.html")

@app.route("/create_course", methods=["POST"])
def create_course(): 
    coursename = request.form["coursename"]
    theory = request.form["theory"]

    sql = "SELECT coursename FROM courses WHERE coursename=:coursename"
    result = db.session.execute(sql, {"coursename":coursename})
    course = result.fetchone()

    if not course:
        sql = "INSERT INTO courses (coursename, theory) VALUES (:coursename, :theory)"
        result = db.session.execute(sql, {"coursename":coursename, "theory":theory})
        db.session.commit()
         
        username = session["username"]
        userid = get_user_id(username)

        coursename = request.form["coursename"]
        courseid = get_course_id(coursename)

        sql = "INSERT INTO users_courses (users_id, courses_id) VALUES (:userid, :courseid)"
        db.session.execute(sql, {"userid":userid, "courseid":courseid})
        db.session.commit()
     
    return redirect("/teachercourses")

@app.route("/edit_course", methods=["POST"])
def editcourse():
    coursename = request.form["coursename"]
    courses_id = request.form["courses_id"]
    sql = "SELECT theory FROM courses WHERE id = :courses_id"
    result = db.session.execute(sql, {"courses_id":courses_id})
    
    theory = result.fetchone()[0]
    theory = theory.split("\n")

    return render_template("editcourse.html", coursename=coursename, courses_id=courses_id, theory=theory)

@app.route("/edit_coursename", methods=["POST"])
def edit_course():
    coursename = request.form["coursename"]
    courses_id = request.form["courses_id"]
    theory = request.form["theory"]

    sql = "UPDATE courses SET coursename = :coursename WHERE id = :courses_id"
    result = db.session.execute(sql, {"coursename":coursename, "courses_id":courses_id})
    db.session.commit()

    sql = "UPDATE courses SET theory = :theory WHERE id = :courses_id"
    result = db.session.execute(sql, {"theory":theory, "courses_id":courses_id})
    db.session.commit()

    return redirect("/teachercourses")

@app.route("/delete_course", methods=["POST"])
def delete_course():
    course_id = request.form["courses_id"]
    coursename = request.form["coursename"]

    try:
        sql = "SELECT id FROM exercises WHERE courses_id = :course_id"
        result = db.session.execute(sql, {"course_id":course_id})
        allexercises = result.fetchall()

        if (len(allexercises) > 0):
            for i in range(0, len(allexercises)):
                exid = allexercises[i]
                exid=exid[0] 
                
                sql = "DELETE FROM answers choices WHERE exercises_id = :exid"
                result = db.session.execute(sql, {"exid":exid})
                db.session.commit() 

                sql = "DELETE FROM choices WHERE exercises_id = :exid"
                result = db.session.execute(sql, {"exid":exid})
                db.session.commit() 
                               
                print("Course deleted succesfully")
    except AttributeError:
        print("Course not deleted")

    sql = "DELETE FROM courses WHERE id = :course_id AND coursename = :coursename"
    result = db.session.execute(sql, {"course_id":course_id, "coursename":coursename})
    db.session.commit()

    return redirect("/teachercourses")

@app.route("/new_exercise", methods=["POST"])
def newexercise():
    coursename = request.form["coursename"]
    courses_id = request.form["courses_id"]
    return render_template("newexercise.html", coursename=coursename, courses_id=courses_id)

@app.route("/create_exercise", methods=["POST"])
def create_exercise():
    username = session["username"]
    userid = get_user_id(username)
    
    coursename = request.form["coursename"]
    courses_id = request.form["courses_id"]
    assignment = request.form["assignment"]

    sql = "INSERT INTO exercises (assignment, courses_id) VALUES (:assignment, :courses_id)"
    result = db.session.execute(sql, {"assignment":assignment, "courses_id":courses_id})
    db.session.commit()
   
    sql = "SELECT id FROM exercises WHERE courses_id=:courses_id AND assignment=:assignment"
    result = db.session.execute(sql, {"courses_id":courses_id, "assignment":assignment})
    exercises_id = result.fetchone().id
   
    choices = request.form.getlist("choice")
    for choice in choices:
        if choice != "":
            sql = "INSERT INTO choices (exercises_id, choice) VALUES (:exercises_id, :choice)"
            db.session.execute(sql, {"exercises_id":exercises_id, "choice":choice})
    db.session.commit()

    finished = False
    sql = "INSERT INTO users_exercises (users_id, courses_id, exercises_id, finished) VALUES (:userid, :courses_id, :exercises_id, :finished)"
    db.session.execute(sql, {"userid":userid, "courses_id":courses_id, "exercises_id":exercises_id, "finished":finished})
    db.session.commit()

    sql = "SELECT id FROM choices WHERE exercises_id=:exercises_id"
    result = db.session.execute(sql, {"exercises_id":exercises_id})
    choices_id = result.fetchone().id

    answer = request.form["answer"]
    sql = "INSERT INTO answers (answer, choices_id, exercises_id) VALUES (:answer, :choices_id, :exercises_id)"
    db.session.execute(sql, {"answer":answer, "choices_id":choices_id, "exercises_id":exercises_id})
    db.session.commit()

    return redirect("/courses/" + coursename)

def get_user_id(username):
    sql = "SELECT id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    userid = result.fetchone().id
    return userid

def get_course_id(coursename):
    sql = "SELECT id FROM courses WHERE coursename=:coursename"
    result = db.session.execute(sql, {"coursename":coursename})
    course_id = result.fetchone().id
    return course_id

def get_user_type(username):
    sql = "SELECT user_type FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user_type = result.fetchone().user_type
    return user_type

@app.route("/")
def frontpage():
    return render_template("index.html") 

