from flask import Flask, render_template
from database import init_database

app = Flask(__name__)

# Initialize database on startup
init_database()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/students')
def students():
    return render_template('students.html')

@app.route('/add_student')
def add_student():
    return render_template('add_student.html')

@app.route('/subjects')
def subjects():
    return render_template('subjects.html')

@app.route('/add_subject')
def add_subject():
    return render_template('add_subject.html')

@app.route('/student/<int:student_id>')
def student(student_id):
    return render_template('student.html')

@app.route('/subject/<int:subject_id>')
def subject(subject_id):
    return render_template('subject.html')


if __name__ == '__main__':
    app.run(debug=True)
