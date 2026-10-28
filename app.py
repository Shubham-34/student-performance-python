"""Student Performance System - Flask + SQLite.

Run:  python app.py      then open http://localhost:5000 in Chrome.
"""
import os
import re
import sqlite3
import time

from flask import (Flask, flash, g, redirect, render_template, request,
                   url_for, abort)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "data", "students.db"))

PASS_MARK = 40
MIN_ATTENDANCE = 75.0
SUBJECTS = ["Mathematics", "Physics", "Chemistry", "English", "Computer Science"]

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production")


# --------------------------------------------------------------- database

def get_db():
    """One SQLite connection per request."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no    TEXT NOT NULL UNIQUE,
    name       TEXT NOT NULL,
    department TEXT,
    email      TEXT,
    attendance REAL NOT NULL DEFAULT 100
);
CREATE TABLE IF NOT EXISTS marks (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    subject    TEXT NOT NULL,
    score      INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
    UNIQUE (student_id, subject)
);
"""

SEED = [
    ("CS101", "Aarav Sharma", "Computer Science", "aarav@example.com", 92.0, [88, 79, 84, 90, 96]),
    ("CS102", "Diya Verma", "Computer Science", "diya@example.com", 96.5, [95, 91, 89, 93, 98]),
    ("CS103", "Rohan Mehta", "Computer Science", "rohan@example.com", 68.0, [52, 38, 45, 61, 70]),
    ("EC201", "Ishita Rao", "Electronics", "ishita@example.com", 84.0, [76, 82, 71, 80, 77]),
    ("EC202", "Kabir Singh", "Electronics", "kabir@example.com", 78.0, [64, 58, 66, 72, 69]),
    ("ME301", "Neha Gupta", "Mechanical", "neha@example.com", 88.0, [81, 85, 78, 74, 83]),
    ("ME302", "Vikram Joshi", "Mechanical", "vikram@example.com", 72.0, [47, 55, 43, 60, 51]),
    ("CE401", "Sana Khan", "Civil", "sana@example.com", 90.0, [73, 69, 75, 82, 79]),
]


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)
    if con.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
        for roll, name, dept, email, att, scores in SEED:
            cur = con.execute(
                "INSERT INTO students (roll_no, name, department, email, attendance) VALUES (?,?,?,?,?)",
                (roll, name, dept, email, att))
            for subject, score in zip(SUBJECTS, scores):
                con.execute("INSERT INTO marks (student_id, subject, score) VALUES (?,?,?)",
                            (cur.lastrowid, subject, score))
    con.commit()
    con.close()


# --------------------------------------------------------- business rules

def grade_for(avg):
    for limit, letter in ((90, "A+"), (80, "A"), (70, "B"), (60, "C"), (50, "D")):
        if avg >= limit:
            return letter
    return "F"


def performance(student, marks):
    """Return a dict with total, average, grade and status for one student."""
    scores = [m["score"] for m in marks]
    if not scores:
        return {"total": 0, "average": 0.0, "grade": "-", "status": "NO DATA"}
    avg = sum(scores) / len(scores)
    if min(scores) < PASS_MARK:
        status = "FAIL"
    elif student["attendance"] < MIN_ATTENDANCE:
        status = "AT RISK"
    else:
        status = "PASS"
    return {"total": sum(scores), "average": avg, "grade": grade_for(avg), "status": status}


def all_students(q="", dept=""):
    db = get_db()
    rows = db.execute("SELECT * FROM students ORDER BY roll_no").fetchall()
    marks_by_student = {}
    for m in db.execute("SELECT * FROM marks ORDER BY subject").fetchall():
        marks_by_student.setdefault(m["student_id"], []).append(m)
    result = []
    q = q.lower()
    for s in rows:
        if dept and s["department"] != dept:
            continue
        if q and q not in s["name"].lower() and q not in s["roll_no"].lower():
            continue
        result.append({"s": s, "perf": performance(s, marks_by_student.get(s["id"], []))})
    return result


# ------------------------------------------------------------------ views

@app.route("/")
def dashboard():
    items = all_students()
    graded = [i for i in items if i["perf"]["status"] != "NO DATA"]
    stats = {
        "count": len(items),
        "average": sum(i["perf"]["average"] for i in graded) / len(graded) if graded else 0,
        "passing": sum(1 for i in graded if i["perf"]["status"] == "PASS"),
        "at_risk": sum(1 for i in graded if i["perf"]["status"] == "AT RISK"),
        "failing": sum(1 for i in graded if i["perf"]["status"] == "FAIL"),
        "topper": max(graded, key=lambda i: i["perf"]["average"]) if graded else None,
    }
    grade_counts = {g: 0 for g in ("A+", "A", "B", "C", "D", "F")}
    for i in graded:
        grade_counts[i["perf"]["grade"]] += 1
    top5 = sorted(graded, key=lambda i: i["perf"]["average"], reverse=True)[:5]
    subject_avgs = get_db().execute(
        "SELECT subject, ROUND(AVG(score), 1) AS average FROM marks GROUP BY subject ORDER BY subject"
    ).fetchall()
    return render_template("dashboard.html", nav="dashboard", stats=stats,
                           grade_counts=grade_counts, top5=top5, subject_avgs=subject_avgs)


@app.route("/students")
def students():
    q = request.args.get("q", "").strip()
    dept = request.args.get("dept", "").strip()
    depts = [r["department"] for r in get_db().execute(
        "SELECT DISTINCT department FROM students WHERE department <> '' ORDER BY department")]
    total = get_db().execute("SELECT COUNT(*) FROM students").fetchone()[0]
    return render_template("students.html", nav="students", items=all_students(q, dept),
                           departments=depts, q=q, dept=dept, total=total)


def validate_student(form, student_id=None):
    data = {
        "roll_no": form.get("roll_no", "").strip(),
        "name": form.get("name", "").strip(),
        "department": form.get("department", "").strip(),
        "email": form.get("email", "").strip(),
        "attendance": form.get("attendance", "").strip(),
    }
    if not data["roll_no"]:
        return data, "Roll number is required."
    if not data["name"]:
        return data, "Name is required."
    try:
        att = float(data["attendance"])
        if not 0 <= att <= 100:
            raise ValueError
    except ValueError:
        return data, "Attendance must be a number between 0 and 100."
    if data["email"] and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", data["email"]):
        return data, "Email address looks invalid."
    clash = get_db().execute(
        "SELECT id FROM students WHERE lower(roll_no) = lower(?) AND id IS NOT ?",
        (data["roll_no"], student_id)).fetchone()
    if clash:
        return data, f"Roll number {data['roll_no']} already exists."
    data["attendance"] = att
    return data, None


@app.route("/students/new", methods=["GET", "POST"])
def student_new():
    if request.method == "POST":
        data, error = validate_student(request.form)
        if error:
            return render_template("student_form.html", nav="students", student=data,
                                   editing=False, error=error)
        db = get_db()
        db.execute("INSERT INTO students (roll_no, name, department, email, attendance) VALUES (?,?,?,?,?)",
                   (data["roll_no"], data["name"], data["department"], data["email"], data["attendance"]))
        db.commit()
        flash(f"Student {data['name']} added.", "ok")
        return redirect(url_for("students"))
    return render_template("student_form.html", nav="students",
                           student={"attendance": 100}, editing=False, error=None)


def get_student_or_404(student_id):
    s = get_db().execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if s is None:
        abort(404)
    return s


@app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
def student_edit(student_id):
    s = get_student_or_404(student_id)
    if request.method == "POST":
        data, error = validate_student(request.form, student_id)
        if error:
            return render_template("student_form.html", nav="students", student=data,
                                   editing=True, error=error, student_id=student_id)
        db = get_db()
        db.execute("UPDATE students SET roll_no=?, name=?, department=?, email=?, attendance=? WHERE id=?",
                   (data["roll_no"], data["name"], data["department"], data["email"],
                    data["attendance"], student_id))
        db.commit()
        flash(f"Student {data['name']} updated.", "ok")
        return redirect(url_for("students"))
    return render_template("student_form.html", nav="students", student=dict(s),
                           editing=True, error=None, student_id=student_id)


@app.route("/students/<int:student_id>")
def student_detail(student_id):
    s = get_student_or_404(student_id)
    marks = get_db().execute("SELECT * FROM marks WHERE student_id = ? ORDER BY subject",
                             (student_id,)).fetchall()
    return render_template("student_detail.html", nav="students", s=s, marks=marks,
                           perf=performance(s, marks), subjects=SUBJECTS, pass_mark=PASS_MARK)


@app.route("/students/<int:student_id>/delete", methods=["POST"])
def student_delete(student_id):
    db = get_db()
    db.execute("DELETE FROM students WHERE id = ?", (student_id,))  # marks removed by CASCADE
    db.commit()
    flash("Student deleted.", "ok")
    return redirect(url_for("students"))


@app.route("/students/<int:student_id>/marks", methods=["POST"])
def mark_save(student_id):
    get_student_or_404(student_id)
    subject = request.form.get("subject", "").strip()
    try:
        score = int(request.form.get("score", ""))
        if not 0 <= score <= 100:
            raise ValueError
    except ValueError:
        flash("Score must be a whole number from 0 to 100.", "error")
        return redirect(url_for("student_detail", student_id=student_id))
    if not subject:
        flash("Subject is required.", "error")
        return redirect(url_for("student_detail", student_id=student_id))
    db = get_db()
    existing = db.execute("SELECT id FROM marks WHERE student_id=? AND lower(subject)=lower(?)",
                          (student_id, subject)).fetchone()
    if existing:
        db.execute("UPDATE marks SET score=? WHERE id=?", (score, existing["id"]))
    else:
        db.execute("INSERT INTO marks (student_id, subject, score) VALUES (?,?,?)",
                   (student_id, subject, score))
    db.commit()
    flash(f"Marks saved for {subject}.", "ok")
    return redirect(url_for("student_detail", student_id=student_id))


@app.route("/marks/<int:mark_id>/delete", methods=["POST"])
def mark_delete(mark_id):
    db = get_db()
    row = db.execute("SELECT student_id FROM marks WHERE id = ?", (mark_id,)).fetchone()
    if row is None:
        abort(404)
    db.execute("DELETE FROM marks WHERE id = ?", (mark_id,))
    db.commit()
    flash("Mark removed.", "ok")
    return redirect(url_for("student_detail", student_id=row["student_id"]))


@app.route("/reports")
def reports():
    db = get_db()
    ranking = db.execute(
        """SELECT s.roll_no, s.name, s.department, COUNT(m.id) AS subjects,
                  SUM(m.score) AS total, ROUND(AVG(m.score), 2) AS average
           FROM students s JOIN marks m ON m.student_id = s.id
           GROUP BY s.id ORDER BY average DESC, s.roll_no""").fetchall()
    subjects = db.execute(
        """SELECT subject, COUNT(*) AS entries, ROUND(AVG(score), 2) AS average,
                  MAX(score) AS highest, MIN(score) AS lowest,
                  SUM(CASE WHEN score >= ? THEN 1 ELSE 0 END) AS passed
           FROM marks GROUP BY subject ORDER BY subject""", (PASS_MARK,)).fetchall()
    departments = db.execute(
        """SELECT s.department, COUNT(DISTINCT s.id) AS students,
                  ROUND(AVG(m.score), 2) AS average, ROUND(AVG(s.attendance), 1) AS attendance
           FROM students s JOIN marks m ON m.student_id = s.id
           GROUP BY s.department ORDER BY average DESC""").fetchall()
    return render_template("reports.html", nav="reports", ranking=ranking,
                           subjects=subjects, departments=departments)


@app.route("/status")
def status():
    db = get_db()
    start = time.perf_counter()
    db.execute("SELECT 1").fetchone()
    millis = (time.perf_counter() - start) * 1000
    info = {
        "sqlite_version": sqlite3.sqlite_version,
        "path": DB_PATH,
        "millis": round(millis, 2),
        "students": db.execute("SELECT COUNT(*) FROM students").fetchone()[0],
        "marks": db.execute("SELECT COUNT(*) FROM marks").fetchone()[0],
    }
    return render_template("status.html", nav="status", info=info)


@app.route("/health")
def health():
    try:
        get_db().execute("SELECT 1").fetchone()
        return "OK"
    except sqlite3.Error:
        return "DB DOWN", 503


@app.errorhandler(404)
def not_found(_e):
    return render_template("error.html", nav="", message="Page or record not found."), 404


init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=True)
