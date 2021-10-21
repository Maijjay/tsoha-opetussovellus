from app import app
from db import db
import routes
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError

def new_user(username, user_type, hash_value):
    try:
        sql = "INSERT INTO users (username, password, user_type) VALUES (:username, :password, :user_type)"
        db.session.execute(sql, {"username":username, "password":hash_value, "user_type":user_type})
        db.session.commit()
        return "Username registered"
    except IntegrityError:
        return "Username already in use"

def check_login(username):
    sql = "SELECT id, password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    return result.fetchone()

def get_user_id(username):
    sql = "SELECT id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    userid = result.fetchone().id
    return userid

def get_user_type(username):
    sql = "SELECT user_type FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user_type = result.fetchone().user_type
    return user_type

def get_all_user_ids_in_course(courses_id):
    sql = "SELECT users_id FROM users_courses WHERE courses_id = :courses_id"
    result = db.session.execute(sql, {"courses_id":courses_id})
    return result.fetchall()

def check_if_joined(userid, courseid):
    sql = "SELECT users_id, courses_id FROM users_courses WHERE (users_id = :userid AND courses_id = :courseid)"
    result = db.session.execute(sql, {"userid":userid, "courseid":courseid})
    return result.fetchone()

def join_new_course(userid, courseid):
    sql = "INSERT INTO users_courses (users_id, courses_id) VALUES (:userid, :courseid)"
    db.session.execute(sql, {"userid":userid, "courseid":courseid})
    db.session.commit()

def get_username(user_id, user_type):
    sql = "SELECT username FROM users WHERE id = :user_id AND user_type = :user_type"
    result = db.session.execute(sql, {"user_id":user_id, "user_type":user_type})
    return result.fetchone()
