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
        unified_card_id,
        phone,
        faculty,
        major,
        year,
        study_schedule,
        years_failed=0,
        admission_type="",
        admission_session="",
        school_study_domain="",
        school_grad_session="",
        school_results=0.0,
        mother_name="",
        father_phone="",
        is_disabled=0,
        social_care_network=0,
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
        self.unified_card_id = unified_card_id
        self.phone = phone
        self.faculty = faculty
        self.major = major
        self.year = int(year) if year is not None else None
        self.study_schedule = study_schedule
        self.admission_session = admission_session
        self.school_study_domain = school_study_domain
        self.school_grad_session = school_grad_session
        self.school_results = school_results
        self.years_failed = years_failed
        self.admission_type = admission_type
        self.mother_name = capitalize_name(mother_name)
        self.father_phone = father_phone
        self.is_disabled = is_disabled
        self.social_care_network = social_care_network
        self.disability = disability
        self.disability_cause = disability_cause
        self.grades = []

    def load_grades(self):
        if self.id is not None:
            self.grades = db_get_grades_by_student_id(self.id)


class Subject:
    def __init__(
        self, semester, code, name, credit_h, structure, prerequisite=None, id=None
    ):
        self.id = id
        self.semester = semester
        self.code = code
        self.name = name
        self.credit_h = credit_h
        self.structure = structure
        self.prerequisite = prerequisite


class Grade:
    def __init__(
        self,
        student_id,
        subject_id,
        semester,
        coursework=0.0,
        final=0.0,
        attended_final=0,
        is_finalized=0,
        last_updated=None,
    ):
        self.student_id = student_id
        self.subject_id = subject_id
        self.semester = semester
        self.coursework = coursework
        self.final = final
        self.attended_final = attended_final
        self.is_finalized = is_finalized
        self.last_updated = last_updated

    def is_failed(self):
        if not self.is_finalized:
            return "no"
        if self.coursework < 13:
            return "coursework"
        if not self.attended_final:
            return "final_attendance"
        if self.final + self.coursework < 50:
            return "final"
        return "no"


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


def db_init():
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
                unified_card_id TEXT UNIQUE NOT NULL,
                phone TEXT UNIQUE NOT NULL,

                faculty TEXT NOT NULL,
                major TEXT NOT NULL,
                year INTEGER,
                study_schedule TEXT NOT NULL,
                years_failed INTEGER NOT NULL DEFAULT 0,
                admission_type TEXT NOT NULL,
                admission_session TEXT NOT NULL,

                school_study_domain TEXT NOT NULL,
                school_grad_session TEXT NOT NULL,
                school_results DECIMAL(5, 2) NOT NULL,

                mother_name TEXT NOT NULL,
                father_phone TEXT NOT NULL,

                is_disabled INTEGER NOT NULL DEFAULT 0,
                social_care_network INTEGER NOT NULL DEFAULT 0,
                disability TEXT,
                disability_cause TEXT
            )
        """)

            # Create subjects table
            cursor.execute("""
            CREATE TABLE subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    semester INTEGER NOT NULL,
                    code TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    credit_h INTEGER NOT NULL,
                    structure TEXT NOT NULL,
                    prerequisite INTEGER,
                    FOREIGN KEY (prerequisite) REFERENCES subjects (id) ON DELETE SET NULL
            )
        """)

            # Create grades table
            cursor.execute("""
            CREATE TABLE grades (
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                semester INTEGER NOT NULL,
                coursework REAL NOT NULL DEFAULT 0.0,
                final REAL NOT NULL DEFAULT 0.0,
                attended_final BOOLEAN NOT NULL DEFAULT 0,
                is_finalized BOOLEAN NOT NULL DEFAULT 0,
                last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

                PRIMARY KEY (student_id, subject_id, semester),
                FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
            )
        """)

        return True
    except Exception:
        return False


def db_get_grades_by_student_id(student_id):
    """Retrieve all grades for a student from the database. Returns list of Grade objects or empty list if error."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT grades.* FROM grades
                JOIN subjects ON grades.subject_id = subjects.id
                WHERE grades.student_id = ?
                ORDER BY grades.semester DESC, subjects.code ASC
                """,
                (student_id,),
            )
            rows = cursor.fetchall()
            return [
                Grade(
                    student_id=row["student_id"],
                    subject_id=row["subject_id"],
                    semester=row["semester"],
                    coursework=row["coursework"],
                    final=row["final"],
                    attended_final=row["attended_final"],
                    is_finalized=row["is_finalized"],
                    last_updated=row["last_updated"],
                )
                for row in rows
            ]
    except Exception:
        return []


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
                    unified_card_id, phone, faculty, major, year, study_schedule,
                    years_failed, admission_type, admission_session, school_study_domain, school_grad_session,
                    school_results, mother_name, father_phone, is_disabled, social_care_network,
                    disability, disability_cause
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    student.name,
                    student.gender,
                    student.nationality,
                    student.birthday,
                    student.ethnicity,
                    student.province,
                    student.unified_card_id,
                    student.phone,
                    student.faculty,
                    student.major,
                    student.year,
                    student.study_schedule,
                    student.years_failed,
                    student.admission_type,
                    student.admission_session,
                    student.school_study_domain,
                    student.school_grad_session,
                    student.school_results,
                    student.mother_name,
                    student.father_phone,
                    student.is_disabled,
                    student.social_care_network,
                    student.disability,
                    student.disability_cause,
                ),
            )
        return True
    except Exception:
        return False


def db_add_grade(
    student_id,
    subject_id,
    semester,
    coursework,
    final,
    attended_final=0,
    is_finalized=0,
):
    """Adds a grade record to the database. Returns True if successful, False if not."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO grades (student_id, subject_id, semester, coursework, final, attended_final, is_finalized)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    student_id,
                    subject_id,
                    semester,
                    coursework,
                    final,
                    attended_final,
                    is_finalized,
                ),
            )
        return True
    except Exception:
        return False


def db_update_grade(
    student_id, subject_id, semester, coursework, final, attended_final, is_finalized
):
    """Updates a grade record in the database. Returns True if successful, False if not."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                UPDATE grades SET semester = ?, coursework = ?, final = ?, attended_final = ?, is_finalized = ?, last_updated = CURRENT_TIMESTAMP
                WHERE student_id = ? AND subject_id = ?
                """,
                (
                    semester,
                    coursework,
                    final,
                    attended_final,
                    is_finalized,
                    student_id,
                    subject_id,
                ),
            )
        return True
    except Exception:
        return False


def db_check_prerequisite(student_id, subject_id, semester):
    """Check if the student has passed the prerequisite in a previous semester. Returns True if satisfied, False otherwise."""
    subject = db_get_subject_by_id(subject_id)
    if not subject or not subject["prerequisite"]:
        return True

    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT grades.* FROM grades
            JOIN subjects ON grades.subject_id = subjects.id
            WHERE grades.student_id = ? AND grades.subject_id = ? AND grades.semester < ?
            """,
            (student_id, subject["prerequisite"], semester),
        )
        rows = cursor.fetchall()
        if not rows:
            return False
        prereq_grade = Grade(
            student_id=rows[0]["student_id"],
            subject_id=rows[0]["subject_id"],
            semester=rows[0]["semester"],
            coursework=rows[0]["coursework"],
            final=rows[0]["final"],
            attended_final=rows[0]["attended_final"],
            is_finalized=rows[0]["is_finalized"],
            last_updated=rows[0]["last_updated"],
        )
        return prereq_grade.is_failed() == "no"


def db_stub():
    """Add fake students and subjects for testing purposes."""
    fake_students = [
        Student(
            name="أحمد محمد علي",
            gender="Male",
            nationality="Iraqi",
            birthday="2002-03-15",
            ethnicity="Arab",
            province="Baghdad",
            unified_card_id="STU001",
            phone="07701234567",
            faculty="Engineering",
            major="Computer Engineering",
            year=2,
            study_schedule="day",
            years_failed=0,
            admission_type="government",
            admission_session="2024/2025",
            school_study_domain="Scientific",
            school_grad_session="2023/2024",
            school_results=85.5,
            mother_name="فاطمة علي",
            father_phone="07709876543",
            is_disabled=0,
            social_care_network=0,
        ),
        Student(
            name="سارة كريم إبراهيم",
            gender="Female",
            nationality="Iraqi",
            birthday="2001-07-22",
            ethnicity="Arab",
            province="Basra",
            unified_card_id="STU002",
            phone="07711234567",
            faculty="Medicine",
            major="General Medicine",
            year=3,
            study_schedule="day",
            years_failed=0,
            admission_type="government",
            admission_session="2023/2024",
            school_study_domain="Scientific",
            school_grad_session="2022/2023",
            school_results=92.0,
            mother_name="ميمونة إبراهيم",
            father_phone="07719876543",
            is_disabled=0,
            social_care_network=0,
        ),
        Student(
            name="محمد حسن حمزة",
            gender="Male",
            nationality="Iraqi",
            birthday="2003-11-10",
            ethnicity="Kurdish",
            province="Erbil",
            unified_card_id="STU003",
            phone="07721234567",
            faculty="Science",
            major="Physics",
            year=1,
            study_schedule="evening",
            years_failed=0,
            admission_type="government",
            admission_session="2025/2026",
            school_study_domain="Scientific",
            school_grad_session="2024/2025",
            school_results=78.5,
            mother_name="رقية حمزة",
            father_phone="07729876543",
            is_disabled=1,
            disability="Hearing impairment",
            disability_cause="Accident",
            social_care_network=1,
        ),
    ]

    for student in fake_students:
        db_add_student(student)

    fake_subjects = [
        Subject(
            semester=1,
            code="CS101",
            name="Introduction to Programming",
            credit_h=4,
            structure="Lecture + Tutorial + Lab",
        ),
        Subject(
            semester=1,
            code="MATH101",
            name="Calculus I",
            credit_h=3,
            structure="Lecture + Tutorial",
        ),
        Subject(
            semester=1,
            code="PHYS101",
            name="Physics I",
            credit_h=3,
            structure="Lecture + Tutorial + Lab",
        ),
        Subject(
            semester=1,
            code="ENG101",
            name="English I",
            credit_h=2,
            structure="Lecture + Tutorial",
        ),
        Subject(
            semester=2,
            code="CS102",
            name="Data Structures",
            credit_h=4,
            structure="Lecture + Tutorial + Lab",
        ),
        Subject(
            semester=2,
            code="MATH102",
            name="Calculus II",
            credit_h=3,
            structure="Lecture + Tutorial",
        ),
        Subject(
            semester=2,
            code="PHYS102",
            name="Physics II",
            credit_h=3,
            structure="Lecture + Tutorial + Lab",
        ),
        Subject(
            semester=2,
            code="ENG102",
            name="English II",
            credit_h=2,
            structure="Lecture + Tutorial",
        ),
    ]

    subject_codes = {}
    for subject in fake_subjects:
        if db_add_subject(subject):
            with get_db_cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM subjects WHERE code = ?", (subject.code,)
                )
                row = cursor.fetchone()
                if row:
                    subject_codes[subject.code] = row["id"]

    prerequisite_map = {
        "CS102": "CS101",
        "MATH102": "MATH101",
        "PHYS102": "PHYS101",
        "ENG102": "ENG101",
    }

    for subject_code, prereq_code in prerequisite_map.items():
        subject_id = subject_codes.get(subject_code)
        prereq_id = subject_codes.get(prereq_code)
        if subject_id and prereq_id:
            with get_db_cursor() as cursor:
                cursor.execute(
                    "UPDATE subjects SET prerequisite = ? WHERE id = ?",
                    (prereq_id, subject_id),
                )

    student_ids = {}
    for student in fake_students:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT id FROM students WHERE unified_card_id = ?",
                (student.unified_card_id,),
            )
            row = cursor.fetchone()
            if row:
                student_ids[student.unified_card_id] = row["id"]

    fake_grades = [
        {
            "student": "STU001",
            "subject": "CS101",
            "semester": 1,
            "coursework": 25.5,
            "final": 58.0,
            "attended_final": 1,
            "is_finalized": 1,
        },
        {
            "student": "STU001",
            "subject": "MATH101",
            "semester": 1,
            "coursework": 22.0,
            "final": 45.0,
            "attended_final": 1,
            "is_finalized": 1,
        },
        {
            "student": "STU001",
            "subject": "PHYS101",
            "semester": 1,
            "coursework": 20.0,
            "final": 52.0,
            "attended_final": 1,
            "is_finalized": 1,
        },
        {
            "student": "STU001",
            "subject": "ENG101",
            "semester": 1,
            "coursework": 18.0,
            "final": 0.0,
            "attended_final": 0,
            "is_finalized": 0,
        },
        {
            "student": "STU001",
            "subject": "CS102",
            "semester": 2,
            "coursework": 15.0,
            "final": 0.0,
            "attended_final": 0,
            "is_finalized": 0,
        },
        {
            "student": "STU001",
            "subject": "MATH102",
            "semester": 2,
            "coursework": 12.0,
            "final": 0.0,
            "attended_final": 0,
            "is_finalized": 0,
        },
        {
            "student": "STU002",
            "subject": "CS101",
            "semester": 1,
            "coursework": 28.0,
            "final": 65.0,
            "attended_final": 1,
            "is_finalized": 1,
        },
        {
            "student": "STU002",
            "subject": "MATH101",
            "semester": 1,
            "coursework": 26.0,
            "final": 60.0,
            "attended_final": 1,
            "is_finalized": 1,
        },
        {
            "student": "STU002",
            "subject": "PHYS101",
            "semester": 1,
            "coursework": 24.0,
            "final": 55.0,
            "attended_final": 1,
            "is_finalized": 1,
        },
        {
            "student": "STU002",
            "subject": "ENG101",
            "semester": 1,
            "coursework": 30.0,
            "final": 70.0,
            "attended_final": 1,
            "is_finalized": 1,
        },
        {
            "student": "STU002",
            "subject": "CS102",
            "semester": 2,
            "coursework": 27.0,
            "final": 62.0,
            "attended_final": 1,
            "is_finalized": 1,
        },
        {
            "student": "STU002",
            "subject": "MATH102",
            "semester": 2,
            "coursework": 25.0,
            "final": 58.0,
            "attended_final": 1,
            "is_finalized": 1,
        },
        {
            "student": "STU003",
            "subject": "CS101",
            "semester": 1,
            "coursework": 10.0,
            "final": 0.0,
            "attended_final": 0,
            "is_finalized": 0,
        },
        {
            "student": "STU003",
            "subject": "MATH101",
            "semester": 1,
            "coursework": 8.0,
            "final": 0.0,
            "attended_final": 0,
            "is_finalized": 0,
        },
        {
            "student": "STU003",
            "subject": "PHYS101",
            "semester": 1,
            "coursework": 12.0,
            "final": 0.0,
            "attended_final": 0,
            "is_finalized": 0,
        },
        {
            "student": "STU003",
            "subject": "ENG101",
            "semester": 1,
            "coursework": 15.0,
            "final": 0.0,
            "attended_final": 0,
            "is_finalized": 0,
        },
    ]

    for grade in fake_grades:
        student_id = student_ids.get(grade["student"])
        subject_id = subject_codes.get(grade["subject"])
        if student_id and subject_id:
            db_add_grade(
                student_id,
                subject_id,
                grade["semester"],
                grade["coursework"],
                grade["final"],
                grade["attended_final"],
                grade["is_finalized"],
            )


def db_del_student(student_id):
    """Deletes a student by student id from the database. Returns True if successful, False if not."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
            return cursor.rowcount > 0
    except Exception:
        return False


def db_edit_student(student):
    """Edits a student in the database. Returns True if successful, False if not."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                UPDATE students SET
                    name = ?, gender = ?, nationality = ?, birthday = ?, ethnicity = ?, province = ?,
                    unified_card_id = ?, phone = ?, faculty = ?, major = ?, year = ?, study_schedule = ?,
                    years_failed = ?, admission_type = ?, admission_session = ?, school_study_domain = ?, school_grad_session = ?,
                    school_results = ?, mother_name = ?, father_phone = ?, is_disabled = ?, social_care_network = ?,
                    disability = ?, disability_cause = ?
                WHERE id = ?
                """,
                (
                    student.name,
                    student.gender,
                    student.nationality,
                    student.birthday,
                    student.ethnicity,
                    student.province,
                    student.unified_card_id,
                    student.phone,
                    student.faculty,
                    student.major,
                    student.year,
                    student.study_schedule,
                    student.years_failed,
                    student.admission_type,
                    student.admission_session,
                    student.school_study_domain,
                    student.school_grad_session,
                    student.school_results,
                    student.mother_name,
                    student.father_phone,
                    student.is_disabled,
                    student.social_care_network,
                    student.disability,
                    student.disability_cause,
                    student.id,
                ),
            )
        return True
    except Exception:
        return False


def db_add_subject(subject):
    """Adds a subject to the database. Returns True if successful, False if not."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO subjects (semester, code, name, credit_h, structure, prerequisite)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    subject.semester,
                    subject.code,
                    subject.name,
                    subject.credit_h,
                    subject.structure,
                    subject.prerequisite,
                ),
            )
        return True
    except Exception:
        return False


def db_get_all_subjects():
    """Retrieve all subjects from the database sorted by semester. Returns list of subjects or empty list if error."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM subjects ORDER BY semester ASC, code ASC")
            return cursor.fetchall()
    except Exception:
        return []


def db_get_subject_by_id(subject_id):
    """Retrieve a single subject by ID. Returns subject dict or None if not found."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,))
            return cursor.fetchone()
    except Exception:
        return None


def db_edit_subject(subject):
    """Updates a subject in the database. Returns True if successful, False if not."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                UPDATE subjects 
                SET semester = ?, code = ?, name = ?, credit_h = ?, structure = ?, prerequisite = ?
                WHERE id = ?
                """,
                (
                    subject.semester,
                    subject.code,
                    subject.name,
                    subject.credit_h,
                    subject.structure,
                    subject.prerequisite,
                    subject.id,
                ),
            )
        return True
    except Exception:
        return False


def db_del_subject(subject_id):
    """Deletes a subject from the database. Returns True if successful, False if not."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        return True
    except Exception:
        return False


def db_check_is_prerequisite_for_later_semester(student_id, subject_id, semester):
    """Check if this subject is a prerequisite for any subject the student has in a later semester."""
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM subjects WHERE prerequisite = ?",
            (subject_id,),
        )
        dependent_subjects = cursor.fetchall()

        if not dependent_subjects:
            return True

        dependent_ids = [s["id"] for s in dependent_subjects]

        placeholders = ",".join("?" * len(dependent_ids))
        cursor.execute(
            f"SELECT * FROM grades WHERE student_id = ? AND subject_id IN ({placeholders}) AND semester > ?",
            (student_id, *dependent_ids, semester),
        )
        later_grades = cursor.fetchall()

        return len(later_grades) == 0


def db_del_grade(student_id, subject_id, semester):
    """Deletes a grade record from the database. Returns True if successful, False if not."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "DELETE FROM grades WHERE student_id = ? AND subject_id = ? AND semester = ?",
                (student_id, subject_id, semester),
            )
        return True
    except Exception:
        return False
