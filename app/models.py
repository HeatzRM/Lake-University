from datetime import datetime
from time import time
from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

@login.user_loader
def load_user(id):
	return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    
    firstname = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    contact = db.Column(db.String(255))
    address = db.Column(db.Text())
    student_transactions = db.relationship('StudentTransaction', backref='user')
    subjects = db.relationship('Subject', backref='user')
    '''
    The four codes specified in ISO/IEC 5218 are:
        0 = not known,
        1 = male,
        2 = female,
        9 = not applicable.
    '''
    sex = db.Column(db.Integer, nullable=False)

    '''
        0 - student
        1 - admin
    '''
    access_level = db.Column(db.Integer, nullable=False)

    def __repr__(self):
    	  #tells Python how to print objects of this class
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

class StudentTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(255), nullable=False)
    contact_details = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    service_type = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cover_destination = db.Column(db.String(255), nullable=False)

class WebsiteData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text, nullable=False)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text, nullable=False)
    

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(255), nullable=False)
    units = db.Column(db.String(255), nullable=False)
    year = db.Column(db.String(255), nullable=False)
    semester = db.Column(db.String(255), nullable=False)
    final_grade = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
