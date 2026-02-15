from flask import Flask, render_template, request, redirect, url_for, flash
from database import (
    db_init,
    db_add_student,
    db_get_all_students,
    db_get_student_by_id,
    db_del_student,
    db_edit_student,
    db_get_all_subjects,
    db_add_subject,
    db_get_subject_by_id,
    db_edit_subject,
    db_del_subject,
    db_get_grades_by_student_id,
    db_add_grade,
    db_update_grade,
    db_del_grade,
    db_check_prerequisite,
    db_check_is_prerequisite_for_later_semester,
    Student,
    Subject,
    Grade,
    db_stub,
)

app = Flask(__name__)

# Initialize database on startup
db_init()
# db_stub()


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
                unified_card_id=request.form["unified_card_id"],
                phone=request.form["phone"],
                faculty=request.form["faculty"],
                major=request.form["major"],
                year=request.form["year"],
                study_schedule=request.form["study_schedule"],
                years_failed=int(request.form["years_failed"])
                if request.form["years_failed"]
                else 0,
                admission_type=request.form["admission_type"],
                admission_session=request.form["admission_session"],
                school_study_domain=request.form["school_study_domain"],
                school_grad_session=request.form["school_grad_session"],
                school_results=float(request.form["school_results"])
                if request.form["school_results"]
                else 0.0,
                mother_name=request.form["mother_name"],
                father_phone=request.form["father_phone"],
                is_disabled=int(request.form["is_disabled"])
                if request.form["is_disabled"]
                else 0,
                social_care_network=int(request.form["social_care_network"])
                if request.form["social_care_network"]
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
                    alert_message="Failed to add student. Ensure the data is correct.",
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
    subjects_data = db_get_all_subjects()
    return render_template("subjects.html", subjects=subjects_data)


@app.route("/add_subject", methods=["GET", "POST"])
def add_subject():
    if request.method == "POST":
        prerequisite = request.form.get("prerequisite")
        if prerequisite == "":
            prerequisite = None

        subject = Subject(
            semester=request.form["semester"],
            code=request.form["code"],
            name=request.form["name"],
            credit_h=request.form["credit_h"],
            structure=request.form["structure"],
            prerequisite=prerequisite,
        )

        success = db_add_subject(subject)

        if success:
            return render_template(
                "add_subject.html",
                alert_type="success",
                alert_message="Subject added successfully!",
                subjects=db_get_all_subjects(),
            )
        else:
            return render_template(
                "add_subject.html",
                alert_type="danger",
                alert_message="Failed to add subject. The subject code may already exist.",
                subjects=db_get_all_subjects(),
            )

    return render_template("add_subject.html", subjects=db_get_all_subjects())


@app.route("/subject/<int:subject_id>")
def view_subject(subject_id):
    subject_data = db_get_subject_by_id(subject_id)
    all_subjects = db_get_all_subjects()
    prerequisite_name = ""
    if subject_data and subject_data["prerequisite"]:
        prereq = db_get_subject_by_id(subject_data["prerequisite"])
        if prereq:
            prerequisite_name = f"{prereq['code']} - {prereq['name']}"
    return render_template(
        "subject.html",
        subject=subject_data,
        prerequisite_name=prerequisite_name,
        all_subjects=all_subjects,
    )


@app.route("/edit_subject/<int:subject_id>", methods=["GET", "POST"])
def edit_subject(subject_id):
    subject_data = db_get_subject_by_id(subject_id)
    all_subjects = db_get_all_subjects()

    if request.method == "POST":
        prerequisite = request.form.get("prerequisite")
        if prerequisite == "":
            prerequisite = None

        subject = Subject(
            id=subject_id,
            semester=request.form["semester"],
            code=request.form["code"],
            name=request.form["name"],
            credit_h=request.form["credit_h"],
            structure=request.form["structure"],
            prerequisite=prerequisite,
        )

        success = db_edit_subject(subject)

        if success:
            return redirect(
                url_for(
                    "view_subject",
                    subject_id=subject_id,
                    alert_type="success",
                    alert_message="Subject updated successfully!",
                )
            )
        else:
            return render_template(
                "edit_subject.html",
                subject=subject_data,
                all_subjects=all_subjects,
                alert_type="danger",
                alert_message="Failed to update subject. The subject code may already exist.",
            )

    return render_template(
        "edit_subject.html", subject=subject_data, all_subjects=all_subjects
    )


@app.route("/delete_subject/<int:subject_id>", methods=["POST"])
def delete_subject(subject_id):
    subject = db_get_subject_by_id(subject_id)
    subject_name = subject["name"] if subject else "Subject"
    db_del_subject(subject_id)
    subjects_data = db_get_all_subjects()
    return render_template(
        "subjects.html",
        subjects=subjects_data,
        alert_type="success",
        alert_message=f"{subject_name} deleted successfully!",
    )


@app.route("/student/<int:student_id>")
def student(student_id):
    student_data = db_get_student_by_id(student_id)
    alert_type = request.args.get("alert_type")
    alert_message = request.args.get("alert_message")
    return render_template(
        "student.html",
        student=student_data,
        alert_type=alert_type,
        alert_message=alert_message,
    )


@app.route("/delete_student/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    student = db_get_student_by_id(student_id)
    student_name = student["name"] if student else "Student"
    db_del_student(student_id)
    students_data = db_get_all_students()
    return render_template(
        "students.html",
        students=students_data,
        alert_type="success",
        alert_message=f"{student_name} deleted successfully!",
    )


@app.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    student_data = db_get_student_by_id(student_id)

    if request.method == "POST":
        try:
            student = Student(
                id=student_id,
                name=request.form["name"],
                gender=request.form["gender"],
                nationality=request.form["nationality"],
                birthday=request.form["birthday"],
                ethnicity=request.form["ethnicity"],
                province=request.form["province"],
                unified_card_id=request.form["unified_card_id"],
                phone=request.form["phone"],
                faculty=request.form["faculty"],
                major=request.form["major"],
                year=request.form["year"],
                study_schedule=request.form["study_schedule"],
                years_failed=int(request.form["years_failed"])
                if request.form["years_failed"]
                else 0,
                admission_type=request.form["admission_type"],
                admission_session=request.form["admission_session"],
                school_study_domain=request.form["school_study_domain"],
                school_grad_session=request.form["school_grad_session"],
                school_results=float(request.form["school_results"])
                if request.form["school_results"]
                else 0.0,
                mother_name=request.form["mother_name"],
                father_phone=request.form["father_phone"],
                is_disabled=int(request.form["is_disabled"])
                if request.form["is_disabled"]
                else 0,
                social_care_network=int(request.form["social_care_network"])
                if request.form["social_care_network"]
                else 0,
                disability=request.form.get("disability", ""),
                disability_cause=request.form.get("disability_cause", ""),
            )

            success = db_edit_student(student)
            if success:
                return redirect(
                    url_for(
                        "student",
                        student_id=student_id,
                        alert_type="success",
                        alert_message="Student updated successfully!",
                    )
                )
            else:
                return render_template(
                    "edit_student.html",
                    student=student_data,
                    alert_type="danger",
                    alert_message="Failed to update student. Ensure the data is correct.",
                )
        except Exception as e:
            return render_template(
                "edit_student.html",
                student=student_data,
                alert_type="danger",
                alert_message=f"Error: {str(e)}",
            )

    return render_template("edit_student.html", student=student_data)


@app.route("/grades/<int:student_id>")
def grades(student_id):
    student_data = db_get_student_by_id(student_id)
    if not student_data:
        return redirect(url_for("students"))

    grades = db_get_grades_by_student_id(student_id)
    grades_with_subjects = []
    for grade in grades:
        subject = db_get_subject_by_id(grade.subject_id)
        grades_with_subjects.append({"grade": grade, "subject": subject})

    alert_type = request.args.get("alert_type")
    alert_message = request.args.get("alert_message")

    return render_template(
        "grades.html",
        student=student_data,
        grades_with_subjects=grades_with_subjects,
        alert_type=alert_type,
        alert_message=alert_message,
    )


@app.route("/update_grade/<int:student_id>/<int:subject_id>", methods=["POST"])
def update_grade(student_id, subject_id):
    semester = int(request.form.get("semester", 1))
    coursework = float(request.form.get("coursework", 0))
    final = float(request.form.get("final", 0))
    attended_final = 1 if request.form.get("attended_final") else 0
    is_finalized = 1 if request.form.get("is_finalized") else 0

    db_update_grade(
        student_id,
        subject_id,
        semester,
        coursework,
        final,
        attended_final,
        is_finalized,
    )

    return redirect(url_for("grades", student_id=student_id))


@app.route("/add_grade/<int:student_id>", methods=["GET", "POST"])
def add_grade(student_id):
    student_data = db_get_student_by_id(student_id)
    if not student_data:
        return redirect(url_for("students"))

    subjects = db_get_all_subjects()

    if request.method == "POST":
        subject_id = int(request.form.get("subject_id"))
        semester = int(request.form.get("semester"))
        coursework = float(request.form.get("coursework", 0))
        final = float(request.form.get("final", 0))
        attended_final = 1 if request.form.get("attended_final") else 0
        is_finalized = 1 if request.form.get("is_finalized") else 0

        if not db_check_prerequisite(student_id, subject_id, semester):
            prereq_subject = db_get_subject_by_id(subject_id)
            prereq = (
                db_get_subject_by_id(prereq_subject["prerequisite"])
                if prereq_subject and prereq_subject["prerequisite"]
                else None
            )
            prereq_name = (
                f"{prereq['code']} - {prereq['name']}" if prereq else "Prerequisite"
            )
            return render_template(
                "add_grade.html",
                student=student_data,
                subjects=subjects,
                alert_type="danger",
                alert_message=f"Cannot add grades. Student must pass {prereq_name} in a previous semester first.",
            )

        success = db_add_grade(
            student_id,
            subject_id,
            semester,
            coursework,
            final,
            attended_final,
            is_finalized,
        )
        if success:
            return redirect(
                url_for(
                    "grades",
                    student_id=student_id,
                    alert_type="success",
                    alert_message="Grade added successfully!",
                )
            )
        else:
            return render_template(
                "add_grade.html",
                student=student_data,
                subjects=subjects,
                alert_type="danger",
                alert_message="Failed to add grade. This entry may already exist.",
            )

    return render_template("add_grade.html", student=student_data, subjects=subjects)


@app.route(
    "/delete_grade/<int:student_id>/<int:subject_id>/<int:semester>", methods=["POST"]
)
def delete_grade(student_id, subject_id, semester):
    if not db_check_is_prerequisite_for_later_semester(
        student_id, subject_id, semester
    ):
        subject = db_get_subject_by_id(subject_id)
        subject_name = (
            f"{subject['code']} - {subject['name']}" if subject else "This subject"
        )
        return redirect(
            url_for(
                "grades",
                student_id=student_id,
                alert_type="danger",
                alert_message=f"Cannot delete grade. {subject_name} is a prerequisite for subjects in later semesters.",
            )
        )

    success = db_del_grade(student_id, subject_id, semester)
    if success:
        return redirect(
            url_for(
                "grades",
                student_id=student_id,
                alert_type="success",
                alert_message="Grade deleted successfully!",
            )
        )
    else:
        return redirect(
            url_for(
                "grades",
                student_id=student_id,
                alert_type="danger",
                alert_message="Failed to delete grade.",
            )
        )


@app.route("/subject/<int:subject_id>")
def subject(subject_id):
    return render_template("subject.html")


if __name__ == "__main__":
    app.run(debug=True)
