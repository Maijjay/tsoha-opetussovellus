from app import app
from db import db
import users
import courses
import exercises
from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError

@app.route("/register" ,methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    password2 = request.form["password"]
    user_type = request.form["user_type"]

    if password == password2:
        hash_value = generate_password_hash(password)
        sql = users.new_user(username, user_type, hash_value)

    return redirect("/")

@app.route("/login" ,methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = users.check_login(username)

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
    user_type = users.get_user_type(username)

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
    user_type = users.get_user_type(username)
    if user_type == 'opiskelija':
        return redirect("/courses")

    user_id = users.get_user_id(username)
    courselist = courses.get_teachers_courses(user_id)
    print(courselist)

    return render_template("teachercourses.html", count=len(courselist), courselist = courselist)

@app.route("/participants", methods=["POST"])
def participants():
    coursename = request.form["coursename"]
    courses_id = request.form["courses_id"]

    all_users_id = users.get_all_user_ids_in_course(courses_id)
    user_exercise_list = []

    for i in range(0, len(all_users_id)):
        user_id = all_users_id[i]
        user_id =user_id[0]
        user_type = "opiskelija"
        username = users.get_username(user_id, user_type)
        finished = True
        
        done_exercises = exercises.get_done_exercises(user_id, courses_id, finished)
        done_exercises = len(done_exercises)

        all_exercises = exercises.get_all_exercises(courses_id)

        if username is not None:
            username = username[0]
            user_exercise_list.append([username, done_exercises])

    return render_template("participants.html", coursename=coursename, user_exercise_list=user_exercise_list, all_exercises=len(all_exercises))

@app.route("/courses")
def student_courses():
    username = session["username"]
    user_type = users.get_user_type(username)
    if user_type == 'opettaja':
        return redirect("/teachercourses")

    all_courses = courses.get_all_coursenames()
    user_id = users.get_user_id(username)
    joined = courses.get_users_courses(user_id)

    return render_template("courses.html", count=len(all_courses), courses=all_courses, joined_count=len(joined), joined=joined)

@app.route("/courses/<coursename>", methods=["GET"])
def coursepage(coursename):

    theory = courses.get_theory(coursename)
    theory = theory[0]
    theorylines = theory.split("\n")

    
    courses_id = courses.get_course_id(coursename)
    username = session["username"]
    user_id = users.get_user_id(username)
    done_exercises = 0
    exerciseslist = []
    try:
        
        allexercises = exercises.get_all_exercises(courses_id)

        if (len(allexercises) > 0):
            exercises_id = []

            for i in range(0, len(allexercises)):
                exid = allexercises[i]
                exid=exid[0] 
                finished = False
            
                exid = exercises.get_users_not_done_exercise_id(user_id, exid, finished)
                
                if exid is not None:
                    exercises_id.append(exid)

            done_exercises = len(allexercises) - len(exercises_id)
            
            for i in range(0, len(exercises_id)):
                exid = exercises_id[i]
                exid=exid[0]

                assignment = exercises.get_exercise_assignment(exid)
                choices = exercises.get_exercise_choices(exid)
                
                for j in range(0, len(choices)):
                    choices[j] = choices[j][0]
                exerciseslist.append([exid, assignment, choices])
                
    except AttributeError:
        return render_template("course.html", coursename=coursename, theorylines=theorylines)         
    
    return render_template("course.html", coursename=coursename, theorylines=theorylines, exercises=exerciseslist, exercises_count=len(allexercises), done_exercises=done_exercises)

@app.route("/answer", methods=["POST"])
def answer():
    answer = request.form["answer"]
    exercises_id = request.form["exercises_id"]
    coursename = request.form["coursename"]

    try:
        is_answer_correct = exercises.get_answer_id(answer, exercises_id)
        course_id = courses.get_course_id(coursename)

        username = session["username"]
        user_id = users.get_user_id(username)

        sql = exercises.set_exercise_done(user_id, course_id ,exercises_id)
    except AttributeError:
        print("Wrong answer")

    return redirect("/courses/" + coursename)

@app.route("/join_course", methods=["POST"])
def join_course():

    username = session["username"]
    user_id = users.get_user_id(username)
    
    coursename = request.form["coursename"]
    course_id = courses.get_course_id(coursename)

    joined = users.check_if_joined(user_id, course_id)

    if not joined:
        sql = users.join_new_course(user_id, course_id)
        
        all_exercise_ids = exercises.get_all_exercises(course_id)

        for ex in all_exercise_ids:
            ex = ex[0]
            if ex != "":
                finished = False
                sql = exercises.add_exercise_to_user(user_id, course_id, ex, finished)

    return redirect("/courses")

@app.route("/leave_course", methods=["POST"])
def leave_course():

    username = session["username"]
    users_id = users.get_user_id(username)

    coursename = request.form["coursename"]
    courses_id = courses.get_course_id(coursename)

    sql = courses.remove_user_from_course(courses_id, users_id)

    return redirect("/courses")

@app.route("/newcourse")
def newcourse():
    return render_template("newcourse.html")

@app.route("/create_course", methods=["POST"])
def create_course(): 
    coursename = request.form["coursename"]
    theory = request.form["theory"]

    course = courses.check_if_coursename_exists(coursename)

    if not course:
        sql = courses.add_new_course(coursename, theory)
        username = session["username"]
        user_id = users.get_user_id(username)

        coursename = request.form["coursename"]
        course_id = courses.get_course_id(coursename)

        #Add teachers user_id to course
        sql = users.join_new_course(user_id, course_id)
     
    return redirect("/teachercourses")

@app.route("/edit_course", methods=["POST"])
def editcourse():
    coursename = request.form["coursename"]
    courses_id = request.form["courses_id"]
    
    theory = courses.get_theory(coursename)
    theory = theory[0]
    theory = theory.split("\n")

    return render_template("editcourse.html", coursename=coursename, courses_id=courses_id, theory=theory)

@app.route("/edit_coursename", methods=["POST"])
def edit_course():
    coursename = request.form["coursename"]
    courses_id = request.form["courses_id"]
    theory = request.form["theory"]
    print(type(coursename))
    print(type(theory))
    if len(coursename) != 0:
        sql = courses.edit_coursename(coursename, courses_id)
    if  len(theory) != 0:
        sql = courses.edit_course_theory(theory, courses_id)

    return redirect("/teachercourses")

@app.route("/delete_course", methods=["POST"])
def delete_course():
    course_id = request.form["courses_id"]
    coursename = request.form["coursename"]

    try:
        
        all_exercises_ids = exercises.get_all_exercises(course_id)

        if (len(all_exercises_ids) > 0):
            for i in range(0, len(all_exercises_ids)):
                exid = all_exercises_ids[i]
                exid=exid[0] 
                
                sql = exercises.delete_exercises_answer(exid)
                sql = exercises.delete_exercises_choices(exid)
                               
                print("Course deleted succesfully")
    except AttributeError:
        print("Course not deleted")

    sql = courses.delete_course(course_id, coursename)

    return redirect("/teachercourses")

@app.route("/new_exercise", methods=["POST"])
def newexercise():
    coursename = request.form["coursename"]
    courses_id = request.form["courses_id"]
    return render_template("newexercise.html", coursename=coursename, courses_id=courses_id)

@app.route("/create_exercise", methods=["POST"])
def create_exercise():
    username = session["username"]
    user_id = users.get_user_id(username)
    
    coursename = request.form["coursename"]
    course_id = request.form["courses_id"]
    assignment = request.form["assignment"]

    sql = exercises.new_exercise(assignment, course_id)
    exercises_id = exercises.get_exercise_id(course_id, assignment)
   
    choices = request.form.getlist("choice")
    for choice in choices:
        if choice != "":
            sql = exercises.new_choises_to_exercise(exercises_id, choice)

    finished = False
    sql = exercises.add_exercise_to_user(user_id, course_id, exercises_id, finished)

    choices_id = exercises.get_choices_id(exercises_id)

    answer = request.form["answer"]

    sql = exercises.new_answer_to_exercise(answer, choices_id, exercises_id)

    return redirect("/courses/" + coursename)

@app.route("/")
def frontpage():
    return render_template("index.html") 






