from app import app
from db import db
import users
import courses
from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash


def new_exercise(assignment, courses_id):
    sql = "INSERT INTO exercises (assignment, courses_id) VALUES (:assignment, :courses_id)"
    result = db.session.execute(sql, {"assignment":assignment, "courses_id":courses_id})
    return db.session.commit()

def new_choises_to_exercise(exercises_id, choice):
    sql = "INSERT INTO choices (exercises_id, choice) VALUES (:exercises_id, :choice)"
    db.session.execute(sql, {"exercises_id":exercises_id, "choice":choice})
    return db.session.commit()

def new_answer_to_exercise(answer, choices_id, exercises_id):
    sql = "INSERT INTO answers (answer, choices_id, exercises_id) VALUES (:answer, :choices_id, :exercises_id)"
    db.session.execute(sql, {"answer":answer, "choices_id":choices_id, "exercises_id":exercises_id})
    return db.session.commit()

def get_exercise_id(courses_id, assignment):
    sql = "SELECT id FROM exercises WHERE courses_id=:courses_id AND assignment=:assignment"
    result = db.session.execute(sql, {"courses_id":courses_id, "assignment":assignment})
    return result.fetchone().id

def get_users_not_done_exercise_id(user_id, exid, finished):
    sql = "SELECT exercises_id FROM users_exercises WHERE users_id = :user_id AND exercises_id = :exid AND finished = :finished"
    result = db.session.execute(sql, {"user_id":user_id, "exid":exid, "finished":finished})
    return result.fetchone()

def get_done_exercises(user_id, courses_id, finished):
    sql = "SELECT finished FROM users_exercises WHERE users_id = :user_id AND courses_id = :courses_id AND finished = :finished"
    result = db.session.execute(sql, {"user_id":user_id, "courses_id":courses_id, "finished":finished})
    return result.fetchall()

def get_all_exercises(courses_id):
    sql = "SELECT id FROM exercises WHERE courses_id = :courses_id"
    result = db.session.execute(sql, {"courses_id":courses_id})
    return result.fetchall()

def get_exercise_assignment(exid):
    sql = "SELECT assignment FROM exercises WHERE id = :exid"
    result = db.session.execute(sql, {"exid":exid})
    return result.fetchone().assignment

def get_exercise_choices(exid):
    sql = "SELECT choice FROM choices WHERE exercises_id = :exid"
    result = db.session.execute(sql, {"exid":exid})
    return result.fetchall()

def get_choices_id(exercises_id):
    sql = "SELECT id FROM choices WHERE exercises_id=:exercises_id"
    result = db.session.execute(sql, {"exercises_id":exercises_id})
    return result.fetchone().id

def get_answer_id(answer, exercises_id):
        sql = "SELECT id FROM answers WHERE answer=:answer AND exercises_id=:exercises_id"
        result = db.session.execute(sql, {"answer":answer, "exercises_id":exercises_id })
        return result.fetchone().id

def set_exercise_done(user_id, course_id, exercises_id):
    sql = "UPDATE users_exercises SET finished = TRUE WHERE users_id = :user_id AND courses_id = :course_id AND exercises_id = :exercises_id"
    db.session.execute(sql, {"user_id":user_id, "course_id":course_id, "exercises_id":exercises_id})
    return db.session.commit() 

def add_exercise_to_user(user_id, course_id, ex, finished):
    sql = "INSERT INTO users_exercises (users_id, courses_id, exercises_id, finished) VALUES (:user_id, :course_id, :ex, :finished)"
    db.session.execute(sql, {"user_id":user_id, "course_id":course_id, "ex":ex, "finished":finished})
    return db.session.commit()

def delete_exercises_answer(exercises_id):
    sql = "DELETE FROM answers choices WHERE exercises_id = :exercises_id"
    result = db.session.execute(sql, {"exercises_id":exercises_id})
    return db.session.commit() 

def delete_exercises_choices(exid):
    sql = "DELETE FROM choices WHERE exercises_id = :exid"
    result = db.session.execute(sql, {"exid":exid})
    return db.session.commit() 
