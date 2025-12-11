from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Association table for many-to-many relationship
teacher_student = db.Table('teacher_student',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True)
)

class Teacher(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    students = db.relationship('Student',secondary=teacher_student, backref='teacher', lazy=True)
    subjects = db.relationship('Subject', backref='teacher', lazy=True)
    marks = db.relationship('Marks', backref='teacher', lazy=True)

    def get_id(self):
        return f'teacher_{self.id}'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Student(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    marks_list = db.relationship('Marks', backref='student', lazy=True)

    def get_id(self):
        return f'student_{self.id}'
    
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)    


class Subject(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)   
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)

    marks = db.relationship('Marks', backref='subject', lazy=True)
 

class Marks(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    marks = db.Column(db.Float, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)