from app import app
from flask_sqlalchemy import SQLAlchemy
from os import getenv

db = SQLAlchemy(app)

app.secret_key = getenv("SECRET_KEY") 

# Fix db sql alchemy not accepting postgres://
db_uri = getenv("DATABASE_URL")
if db_uri.startswith("postgres://"):
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
