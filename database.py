import sqlite3
import os
from contextlib import contextmanager

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

# CLASSES
class Student:
    # TODO:
    pass

class Subject:
    # TODO:
    pass


# GENERAL
def get_db_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def get_db_cursor():
    """Context manager for database operations."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_database():
    """Initialize the database with required tables."""
    with get_db_cursor() as cursor:
        cursor.execute('''
            CREATE TABLE students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,
                gender TEXT NOT NULL,
                nationality TEXT NOT NULL,
                birthday TEXT NOT NULL,
                tribe TEXT NOT NULL,
                province TEXT NOT NULL,
                card_num TEXT UNIQUE NOT NULL,
                phone TEXT UNIQUE NOT NULL,

                faculty TEXT NOT NULL,
                major TEXT NOT NULL,
                study_year TEXT NOT NULL,
                study_type TEXT NOT NULL,
                years_failed INTEGER NOT NULL DEFAULT 0,
                admission_year TEXT NOT NULL,

                school_type TEXT NOT NULL,
                school_graduation TEXT NOT NULL,
                school_result DECIMAL(5, 2) NOT NULL,

                mother_name TEXT NOT NULL,
                father_phone TEXT NOT NULL,

                is_disabled INTEGER NOT NULL DEFAULT 0,
                disability TEXT,
                disability_cause TEXT
            )

            CREATE TABLE subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    year INTEGER NOT NULL,
                    semester INTEGER NOT NULL,

                    code TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    language TEXT NOT NULL
            )

            CREATE TABLE subject_prerequisites (
                subject_id INTEGER NOT NULL,
                prerequisite_id INTEGER NOT NULL,

                PRIMARY KEY (subject_id, prerequisite_id),
                FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE,
                FOREIGN KEY (prerequisite_id) REFERENCES subjects (id) ON DELETE CASCADE
            )

            CREATE TABLE enrollments (
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,

                PRIMARY KEY (student_id, subject_id),
                FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
            )

            CREATE TABLE grades (
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                coursework REAL NOT NULL DEFAULT 0.0,
                final REAL NOT NULL DEFAULT 0.0,

                PRIMARY KEY (student_id, subject_id),
                FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
            )
        ''')

# STUDENTS FUNCTIONS
def get_students(name):
    """Retrieve students by name from the database."""

def add_student(student):
    """Adds a student to the database."""

def del_student(student_id):
    """Deletes a student by student id from the database."""

def edit_student(student_id):
    """Edits a student from the database."""

# SUBJECT FUNCTIONS
def get_all_subjects():
    """Retrieve all subjects from the database."""

def add_subject(subject):
    """Adds a subject to the database."""

def del_subject(subject_id):
    """Deletes a subject by subject id from the database."""

def edit_subject(subject):
    """Edits a subject to the database."""
