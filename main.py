from flask import Flask, render_template, redirect, request, url_for, flash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import check_password_hash
from models import db, Teacher, Student, Subject, Marks
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lms.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["TEACHER_SECRET"] = os.getenv("TEACHER_SECRET", "default_teacher_secret")

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view ='teacher_login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # user_id format: "teacher_1" or "student_1"
    if user_id.startswith('teacher_'):
        return Teacher.query.get(int(user_id.split('_')[1]))
    elif user_id.startswith('student_'):
        return Student.query.get(int(user_id.split('_')[1]))
    return None

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/teacher/register", methods=["GET", "POST"])
def teacher_register():
    if request.method == "POST":
        secret = request.form["secret"]

        if secret != app.config['TEACHER_SECRET']:
            flash("Invalid secret code. You cannot register as a teacher.", "danger")
            return redirect("/teacher/register")
        
        else:
            username = request.form["username"]
            password = request.form["password"]

            existing = Teacher.query.filter_by(username=username).first()
            if existing:
                flash("Invalid username! Try another username", "danger")
                return redirect("/teacher/register")
            new_teacher = Teacher(username=username)
            new_teacher.set_password(password)

            db.session.add(new_teacher)
            db.session.commit()
            flash("Teacher account created successfully", "success")
            return redirect("/teacher/login")

    return render_template("teacher_register.html")

@app.route("/teacher/login", methods=["GET", "POST"])   
def teacher_login():
    if request.method == "POST":
        username = request.form["username"] 
        password = request.form["password"] 

        teacher = Teacher.query.filter_by(username=username).first()
        if teacher and teacher.check_password(password):
            login_user(teacher)
            return redirect(url_for("teacher_dashboard"))
        flash("Invalid credentials!", "danger")

    return render_template("teacher_login.html")

@app.route("/student/login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        student_id = request.form["student_id"]
        password = request.form["password"]
        student = Student.query.filter_by(student_id=student_id).first()

        if student and student.check_password(password):
            login_user(student)
            return redirect(url_for("student_dashboard"))
        flash("Invalid credentials!", "danger")
    return render_template("student_login.html")
    
@app.route("/teacher/dashboard")    
@login_required
def teacher_dashboard():
    if not isinstance(current_user, Teacher):
        return "Unauthorized", 403
    
    students = current_user.students
    subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
    return render_template("teacher_dashboard.html", students=students, subjects=subjects)

@app.route("/student/dashboard") 
@login_required
def student_dashboard():
    if not isinstance(current_user, Student):
        return "Unauthorized", 403
    marks = Marks.query.filter_by(student_id=current_user.id).all()
    return render_template("student_dashboard.html", marks=marks)

@app.route("/add_student", methods=["GET", "POST"])
@login_required
def add_student():
    if not isinstance(current_user, Teacher):
        return "Unauthorized", 403

    if request.method == "POST":
        name = request.form["name"].strip()
        student_id = request.form["student_id"].strip()
        password = request.form["password"]

        if not student_id:
            flash("Student ID is required.", "danger")
            return redirect("/add_student")
        
        exists = Student.query.filter_by(student_id=student_id).first()
        if exists:
            if exists in current_user.students:
                flash("This student is already added to your account!", "danger")
                return redirect("/add_student")
            else:
                current_user.students.append(exists)
                db.session.commit()
                flash(f"Student {exists.name} added to your account!", "success")
                return redirect("/teacher/dashboard")
        else:
            if not name or not password:
                flash("Name and password are required for new students.", "danger")
                return redirect("/add_student")
            new_student = Student(name=name, student_id=student_id)
            new_student.set_password(password)
            current_user.students.append(new_student)
            db.session.add(new_student)
            db.session.commit()
            flash("New student created and added successfully!", "success")
            return redirect("/teacher/dashboard")
            
    return render_template("add_student.html")    

@app.route("/add_subject", methods=["GET", "POST"])
@login_required
def add_subject():
        if not isinstance(current_user, Teacher):
            return "Unauthorized", 403
        
        if request.method == "POST":
            name = request.form["name"].strip()
            if not name:
                flash("Subject name is required.", "danger")
                return redirect("/add_subject")
            
            exists = Subject.query.filter_by(name=name, teacher_id=current_user.id).first()
            if exists:
                flash("Subject already exists!", "danger")
                return redirect("/add_subject")
            new_subject = Subject(name=name, teacher_id=current_user.id)
            db.session.add(new_subject)
            db.session.commit()
            flash("Subject add successfully", "success")
            return redirect("/teacher/dashboard")
        return render_template("add_subject.html")

@app.route("/add_marks",methods=["GET", "POST"])
@login_required
def add_marks():
        if not isinstance(current_user, Teacher):
            return "Unauthorized", 403
        
        students = current_user.students
        subjects = Subject.query.filter_by(teacher_id=current_user.id).all()

        if request.method == "POST":
            try:
                student_id = int(request.form["student_id"])
                subject_id = int(request.form["subject_id"])
                marks = float(request.form["marks"])
            except(ValueError, KeyError):
                flash("Invalid Input", "danger")
                return redirect("/add_marks")
            
            student = Student.query.get(student_id)
            if not student or student not in current_user.students:
                    flash("Selected student is not in your account.", "danger")
                    return redirect("/add_marks")
        
            subject = Subject.query.filter_by(id=subject_id, teacher_id=current_user.id).first()
            if not subject:
                flash("Selected subject is invalid.", "danger")
                return redirect("/add_marks")

            records = Marks(student_id=student_id,
                    subject_id=subject_id,
                    marks=marks,
                    teacher_id=current_user.id)
            db.session.add(records)
            db.session.commit()
            flash("Marks added!", "success")
            return redirect("/teacher/dashboard")
        return render_template("add_marks.html", students=students, subjects=subjects)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")   


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)