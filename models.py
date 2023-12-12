from flask_sqlalchemy import SQLAlchemy
          
db = SQLAlchemy()
          
class Users(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), index=True, unique=True)
    email = db.Column(db.String(150), index=True, unique=True)
    password = db.Column(db.String(255), index=True, unique=True)

class Stroke(db.Model):
    __tablename__ = "stroke"
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)
    hypertension = db.Column(db.Integer)
    heart_disease = db.Column(db.Integer)
    glucose = db.Column(db.Float)
    bmi = db.Column(db.Float)
    stroke = db.Column(db.Integer)

class Cholesterol(db.Model):
    __tablename__ = "cholesterol"
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)
    sys_bp = db.Column(db.Float)
    dia_bp = db.Column(db.Float)
    bmi = db.Column(db.Float)
    heart_rate = db.Column(db.Integer)
    glucose = db.Column(db.Float)
    tot_chol = db.Column(db.Float)
