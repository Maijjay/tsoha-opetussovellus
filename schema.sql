CREATE TABLE users (
    id SERIAL PRIMARY KEY, 
    username TEXT, 
    password TEXT, 
    user_type TEXT
    );

CREATE TABLE courses (
    id SERIAL PRIMARY KEY, 
    coursename TEXT,
    theory TEXT
    );

CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    assignment TEXT,
    courses_id int REFERENCES courses (id) ON UPDATE CASCADE ON DELETE CASCADE
    );

CREATE TABLE choices (
    id SERIAL PRIMARY KEY,
    exercises_id int REFERENCES exercises,
    choice TEXT
    );

CREATE TABLE answers (
    id SERIAL PRIMARY KEY,
    answer TEXT,
    choices_id int REFERENCES choices,
    exercises_id int REFERENCES exercises
    );

CREATE TABLE users_courses (
    users_id int REFERENCES users (id) ON UPDATE CASCADE ON DELETE CASCADE,
    courses_id int REFERENCES courses (id) ON UPDATE CASCADE ON DELETE CASCADE
    );

CREATE TABLE users_exercises (
    users_id int REFERENCES users (id) ON UPDATE CASCADE ON DELETE CASCADE,
    courses_id int REFERENCES courses (id) ON UPDATE CASCADE ON DELETE CASCADE,
    exercises_id int REFERENCES exercises,
    finished BOOLEAN
    );