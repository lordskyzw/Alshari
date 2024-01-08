from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(100), nullable=False)
    employee = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Plate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_plate = db.Column(db.String(100), nullable=False)
    owner = db.Column(db.String(100), nullable=False)

class RFIDTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rfid = db.Column(db.String(100), nullable=False)
    employee_name = db.Column(db.String(100))