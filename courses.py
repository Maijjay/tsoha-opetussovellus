from db import db
import courses
from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError


def get_course_id(coursename):
    sql = "SELECT id FROM courses WHERE coursename=:coursename"
    result = db.session.execute(sql, {"coursename":coursename})
    course_id = result.fetchone().id
    return course_id

def get_all_coursenames(): # ONKO TARPEELLINEN METODI?
    result = db.session.execute("SELECT coursename FROM courses")
    return result.fetchall()

def get_teachers_courses(user_id):
    # TARVIIKO TÄSSÄ TÄTÄ: courses.id = users_courses.courses_id?
    sql = "SELECT id, coursename FROM courses, users_courses WHERE courses.id = users_courses.courses_id AND users_courses.users_id=:user_id"
    result = db.session.execute(sql, {"user_id":user_id})
    return result.fetchall()

def get_users_courses(user_id):
    sql = "SELECT coursename FROM courses, users_courses WHERE courses.id = users_courses.courses_id AND users_courses.users_id=:user_id"
    result = db.session.execute(sql, {"user_id":user_id})
    return result.fetchall()

def get_theory(coursename):
    sql = "SELECT theory FROM courses WHERE coursename = :coursename"
    result = db.session.execute(sql, {"coursename":coursename})
    return result.fetchone()

def remove_user_from_course(courses_id, users_id):
    sql = "DELETE FROM users_courses WHERE courses_id = :courses_id AND users_id = :users_id"
    result = db.session.execute(sql, {"courses_id":courses_id, "users_id":users_id})
    return db.session.commit()

def check_if_coursename_exists(coursename):
    sql = "SELECT coursename FROM courses WHERE coursename=:coursename"
    result = db.session.execute(sql, {"coursename":coursename})
    return result.fetchone()

def add_new_course(coursename, theory):
    sql = "INSERT INTO courses (coursename, theory) VALUES (:coursename, :theory)"
    result = db.session.execute(sql, {"coursename":coursename, "theory":theory})
    return db.session.commit()

def edit_coursename(coursename, courses_id):
    sql = "UPDATE courses SET coursename = :coursename WHERE id = :courses_id"
    result = db.session.execute(sql, {"coursename":coursename, "courses_id":courses_id})
    return db.session.commit()

def edit_course_theory(theory, courses_id):
    sql = "UPDATE courses SET theory = :theory WHERE id = :courses_id"
    result = db.session.execute(sql, {"theory":theory, "courses_id":courses_id})
    return db.session.commit()

def delete_course(course_id, coursename):
    sql = "DELETE FROM courses WHERE id = :course_id AND coursename = :coursename"
    result = db.session.execute(sql, {"course_id":course_id, "coursename":coursename})
    return db.session.commit()



