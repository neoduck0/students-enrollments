from flask import Flask, render_template, request, redirect, url_for, flash
from database import (
    init_database,
    db_add_student,
    db_get_all_students,
    db_get_student_by_id,
    Student,
)

app = Flask(__name__)

# Initialize database on startup
init_database()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/students")
def students():
    students_data = db_get_all_students()
    return render_template("students.html", students=students_data)


@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        try:
            # Extract form data
            student = Student(
                name=request.form["name"],
                gender=request.form["gender"],
                nationality=request.form["nationality"],
                birthday=request.form["birthday"],
                ethnicity=request.form["ethnicity"],
                province=request.form["province"],
                card_id=request.form["card_id"],
                phone=request.form["phone"],
                faculty=request.form["faculty"],
                major=request.form["major"],
                year=request.form["year"],
                study_schedule=request.form["study_schedule"],
                repeat_years=int(request.form["repeat_years"])
                if request.form["repeat_years"]
                else 0,
                admission_session=request.form["admission_session"],
                school_focus=request.form["school_focus"],
                school_grad_session=request.form["school_grad_session"],
                school_results=float(request.form["school_results"])
                if request.form["school_results"]
                else 0.0,
                mother_name=request.form["mother_name"],
                father_phone=request.form["father_phone"],
                is_disabled=int(request.form["is_disabled"])
                if request.form["is_disabled"]
                else 0,
                disability=request.form.get("disability", ""),
                disability_cause=request.form.get("disability_cause", ""),
            )

            # Add student to database
            success = db_add_student(student)
            if success:
                return render_template(
                    "add_student.html",
                    alert_type="success",
                    alert_message="Student added successfully!",
                )
            else:
                return render_template(
                    "add_student.html",
                    alert_type="danger",
                    alert_message="Failed to add student. Please try again.",
                )
        except Exception as e:
            return render_template(
                "add_student.html",
                alert_type="danger",
                alert_message=f"Error: {str(e)}",
            )

    return render_template("add_student.html")


@app.route("/subjects")
def subjects():
    return render_template("subjects.html")


@app.route("/add_subject")
def add_subject():
    return render_template("add_subject.html")


@app.route("/student/<int:student_id>")
def student(student_id):
    student_data = db_get_student_by_id(student_id)
    return render_template("student.html", student=student_data)


@app.route("/subject/<int:subject_id>")
def subject(subject_id):
    return render_template("subject.html")


if __name__ == "__main__":
    app.run(debug=True)
