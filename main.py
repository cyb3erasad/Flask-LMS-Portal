from flask import Flask, render_template, redirect, request, url_for, flash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import check_password_hash
from models import db, Teacher, Student, Subject, Marks

app = Flask(__name__)

app.config["SECRET_KEY"] = "523764902234"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lms.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['TEACHER_SECRET'] = '6543210987'

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view ='teacher_login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    user = Teacher.query.get(int(user_id))
    if user:
        return user
    else:
        return Student.query.get(int(user_id))

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
        if teacher and check_password_hash(teacher.password, password):
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
    students = Student.query.all()
    subjects = Subject.query.all()
    return render_template("teacher_dashboard.html", students=students, subjects=subjects)

@app.route("/student/dashboard") 
@login_required
def student_dashboard():
    if not isinstance(current_user, Student):
        return "Unauthorized", 403
    marks = Marks.query.filter_by(student_id=current_user.id).first()
    return render_template("student_dashboard.html", marks=marks)

@app.route("/add_student", methods=["GET", "POST"])
@login_required
def add_student():
    if not isinstance(current_user, Teacher):
        return "Unauthorized", 403

    if request.method == "POST":
        name = request.form["name"]
        student_id = request.form["student_id"]
        password = request.form["password"]

        exists = Student.query.filter_by(student_id=student_id).first()
        if exists:
            flash("Student ID already exists!", "danger")
            return redirect("/add_student")

        new_student = Student(name=name, student_id=student_id)
        new_student.set_password(password)

        db.session.add(new_student)
        db.session.commit()
        flash("Student add successfully!", "success")
        return redirect("/teacher/dashboard")
    return render_template("add_student.html")

@app.route("/add_subject", methods=["GET", "POST"])
@login_required
def add_subject():
        if not isinstance(current_user, Teacher):
            return "Unauthorized", 403
        
        if request.method == "POST":
            name = request.form["name"]
            new_subject = Subject(name=name)
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
        
        students = Student.query.all()
        subjects = Subject.query.all()

        if request.method == "POST":
            student_id = request.form["student_id"]
            subject_id = request.form["subject_id"]
            marks = request.form["marks"]

            records = Marks(student_id=student_id,
                        subject_id=subject_id,
                        marks=marks)
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