from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from settings import settings

db = SQLAlchemy()
app = Flask(__name__)
path = settings()["DATABASE_PATH"]
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db.init_app(app)

class Words(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String, unique=True, nullable=False)
    desc = db.Column(db.String)
    prac_time = db.Column(db.Integer)
    practice_point = db.Column(db.Integer)
    search_time = db.Column(db.Integer)

class Pratice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)

with app.app_context():
    db.create_all()