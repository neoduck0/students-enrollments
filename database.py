import sqlite3
import os
from contextlib import contextmanager


def capitalize_name(name):
    """Capitalize a name properly (first letter uppercase, rest lowercase)."""
    if not name or not isinstance(name, str):
        return name
    return " ".join(word.capitalize() for word in name.strip().split())


DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database.db")


# CLASSES
class Student:
    def __init__(
        self,
        name,
        gender,
        nationality,
        birthday,
        ethnicity,
        province,
        card_id,
        phone,
        faculty,
        major,
        year,
        study_schedule,
        repeat_years=0,
        admission_session="",
        school_focus="",
        school_grad_session="",
        school_results=0.0,
        mother_name="",
        father_phone="",
        is_disabled=0,
        disability="",
        disability_cause="",
        id=None,
    ):
        self.id = id
        self.name = capitalize_name(name)
        self.gender = gender
        self.nationality = nationality
        self.birthday = birthday
        self.ethnicity = ethnicity
        self.province = province
        self.card_id = card_id
        self.phone = phone
        self.faculty = faculty
        self.major = major
        self.year = int(year) if year is not None else None
        self.study_schedule = study_schedule
        self.repeat_years = repeat_years
        self.admission_session = admission_session
        self.school_focus = school_focus
        self.school_grad_session = school_grad_session
        self.school_results = school_results
        self.mother_name = capitalize_name(mother_name)
        self.father_phone = father_phone
        self.is_disabled = is_disabled
        self.disability = disability
        self.disability_cause = disability_cause


class Subject:
    def __init__(self, year, semester, code, name, credit_h, structure, id=None):
        self.id = id
        self.year = year
        self.semester = semester
        self.code = code
        self.name = name
        self.credit_h = credit_h
        self.structure = structure


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
    """Initialize the database with required tables. Returns True if successful, False if not."""
    try:
        with get_db_cursor() as cursor:
            # Create students table
            cursor.execute("""
            CREATE TABLE students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,
                gender TEXT NOT NULL,
                nationality TEXT NOT NULL,
                birthday TEXT NOT NULL,
                ethnicity TEXT NOT NULL,
                province TEXT NOT NULL,
                card_id TEXT UNIQUE NOT NULL,
                phone TEXT UNIQUE NOT NULL,

                faculty TEXT NOT NULL,
                major TEXT NOT NULL,
                year INTEGER,
                study_schedule TEXT NOT NULL,
                repeat_years INTEGER NOT NULL DEFAULT 0,
                admission_session TEXT NOT NULL,

                school_focus TEXT NOT NULL,
                school_grad_session TEXT NOT NULL,
                school_results DECIMAL(5, 2) NOT NULL,

                mother_name TEXT NOT NULL,
                father_phone TEXT NOT NULL,

                is_disabled INTEGER NOT NULL DEFAULT 0,
                disability TEXT,
                disability_cause TEXT
            )
        """)

            # Create subjects table
            cursor.execute("""
            CREATE TABLE subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    year INTEGER NOT NULL,
                    semester INTEGER NOT NULL,
                    code TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    credit_h INTEGER NOT NULL,
                    structure TEXT NOT NULL
            )
        """)

            # Create subject_prerequisites table
            cursor.execute("""
            CREATE TABLE subject_prerequisites (
                subject_id INTEGER NOT NULL,
                prerequisite_id INTEGER NOT NULL,

                PRIMARY KEY (subject_id, prerequisite_id),
                FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE,
                FOREIGN KEY (prerequisite_id) REFERENCES subjects (id) ON DELETE CASCADE
            )
        """)

            # Create enrollments table
            cursor.execute("""
            CREATE TABLE enrollments (
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,

                PRIMARY KEY (student_id, subject_id),
                FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
            )
        """)

            # Create grades table
            cursor.execute("""
            CREATE TABLE grades (
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                coursework REAL NOT NULL DEFAULT 0.0,
                final REAL NOT NULL DEFAULT 0.0,

                PRIMARY KEY (student_id, subject_id),
                FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
            )
        """)

        return True
    except Exception:
        return False


# STUDENTS FUNCTIONS
def db_get_students(name):
    """Retrieve students by name from the database. Returns list of students or empty list if error."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM students WHERE name LIKE ?", (f"%{name}%",))
            return cursor.fetchall()
    except Exception:
        return []


def db_get_all_students():
    """Retrieve all students from the database. Returns list of students or empty list if error."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM students ORDER BY name ASC")
            return cursor.fetchall()
    except Exception:
        return []


def db_get_student_by_id(student_id):
    """Retrieve a single student by ID from the database. Returns student data or None if not found."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
            return cursor.fetchone()
    except Exception:
        return None


def db_add_student(student):
    """Adds a student to the database. Returns True if successful, False if not."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO students (
                    name, gender, nationality, birthday, ethnicity, province,
                    card_id, phone, faculty, major, year, study_schedule,
                    repeat_years, admission_session, school_focus, school_grad_session,
                    school_results, mother_name, father_phone, is_disabled,
                    disability, disability_cause
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    student.name,
                    student.gender,
                    student.nationality,
                    student.birthday,
                    student.ethnicity,
                    student.province,
                    student.card_id,
                    student.phone,
                    student.faculty,
                    student.major,
                    student.year,
                    student.study_schedule,
                    student.repeat_years,
                    student.admission_session,
                    student.school_focus,
                    student.school_grad_session,
                    student.school_results,
                    student.mother_name,
                    student.father_phone,
                    student.is_disabled,
                    student.disability,
                    student.disability_cause,
                ),
            )
        return True
    except Exception:
        return False


def add_fake_students():
    """Add fake students for testing purposes."""
    fake_students = [
        Student(
            name="Alice Johnson",
            gender="Female",
            nationality="American",
            birthday="2000-05-15",
            ethnicity="Caucasian",
            province="California",
            card_id="STU001",
            phone="555-0101",
            faculty="Engineering",
            major="Computer Science",
            year=2,
            study_schedule="day",
            repeat_years=0,
            admission_session="2020",
            school_focus="Mathematics",
            school_grad_session="2019",
            school_results=85.5,
            mother_name="Sarah Johnson",
            father_phone="555-0102",
            is_disabled=0,
        ),
        Student(
            name="Bob Smith",
            gender="Male",
            nationality="American",
            birthday="1999-08-22",
            ethnicity="Hispanic",
            province="Texas",
            card_id="STU002",
            phone="555-0201",
            faculty="Business",
            major="Marketing",
            year=3,
            study_schedule="day",
            repeat_years=1,
            admission_session="2019",
            school_focus="Biology",
            school_grad_session="2018",
            school_results=78.0,
            mother_name="Maria Smith",
            father_phone="555-0202",
            is_disabled=0,
        ),
        Student(
            name="Carol Williams",
            gender="Female",
            nationality="Canadian",
            birthday="2001-02-10",
            ethnicity="Native",
            province="Ontario",
            card_id="STU003",
            phone="555-0301",
            faculty="Arts",
            major="English Literature",
            year=1,
            study_schedule="night",
            repeat_years=0,
            admission_session="2021",
            school_focus="Literature",
            school_grad_session="2020",
            school_results=92.3,
            mother_name="Jennifer Williams",
            father_phone="555-0302",
            is_disabled=1,
            disability="Visual impairment",
            disability_cause="Congenital",
        ),
    ]

    for student in fake_students:
        db_add_student(student)


def db_del_student(student_id):
    """Deletes a student by student id from the database. Returns True if successful, False if not."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
            return cursor.rowcount > 0
    except Exception:
        return False


def db_edit_student(student):
    """Edits a student from the database. Returns True if successful, False if not."""
    try:
        # This function needs implementation for actual editing logic
        # For now, return False to indicate not implemented
        return False
    except Exception:
        return False


# SUBJECT FUNCTIONS
def db_get_all_subjects(year=None, semester=None):
    """Retrieve all subjects from the database. Returns list of subjects or empty list if error."""
    try:
        with get_db_cursor() as cursor:
            if year and semester:
                cursor.execute(
                    "SELECT * FROM subjects WHERE year = ? AND semester = ?",
                    (year, semester),
                )
            elif year:
                cursor.execute("SELECT * FROM subjects WHERE year = ?", (year,))
            elif semester:
                cursor.execute("SELECT * FROM subjects WHERE semester = ?", (semester,))
            else:
                cursor.execute("SELECT * FROM subjects")
            return cursor.fetchall()
    except Exception:
        return []


def db_add_subject(subject):
    """Adds a subject to the database. Returns True if successful, False if not."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO subjects (year, semester, code, name, credit_h, structure)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    subject.year,
                    subject.semester,
                    subject.code,
                    subject.name,
                    subject.credit_h,
                    subject.structure,
                ),
            )
            return True
    except Exception:
        return False


def db_del_subject(subject_id):
    """Deletes a subject by subject id from the database. Returns True if successful, False if not."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
            return cursor.rowcount > 0
    except Exception:
        return False


def db_edit_subject(subject):
    """Edits a subject to the database. Returns True if successful, False if not."""
    try:
        # This function needs implementation for actual editing logic
        # For now, return False to indicate not implemented
        return False
    except Exception:
        return False


# CROSS FUNCTIONS
def db_enroll_student(student_id, subject_id):
    """Enrolls a student to a subject. Returns True if successful, False if not."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "INSERT OR IGNORE INTO enrollments (student_id, subject_id) VALUES (?, ?)",
                (student_id, subject_id),
            )
            return cursor.rowcount > 0
    except Exception:
        return False


def db_grade_student(student_id, subject_id, cw_result, f_result):
    """Grades a student in a specific subject. Returns True if successful, False if not."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT OR REPLACE INTO grades (student_id, subject_id, coursework, final)
                VALUES (?, ?, ?, ?)
            """,
                (student_id, subject_id, cw_result, f_result),
            )
            return True
    except Exception:
        return False
