from flask import Flask
from models import db, Teacher, Student, Subject, Marks
import os

# Create a minimal Flask app just for initialization
app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")
app.config["TEACHER_SECRET"] = os.getenv("TEACHER_SECRET", "default_teacher_secret")

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("MYSQL_URL")

if DATABASE_URL:
    if DATABASE_URL.startswith("mysql://"):
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://")
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lms.db'

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize db with this app
db.init_app(app)

print("=" * 50)
print("Starting database initialization...")
print("=" * 50)

try:
    with app.app_context():
        print("Creating all tables...")
        db.create_all()
        print("✅ Database tables created successfully!")
        print("Tables created:", list(db.metadata.tables.keys()))
        print("=" * 50)
except Exception as e:
    print(f"❌ Error creating tables: {e}")
    print("=" * 50)
    import sys
    sys.exit(1)