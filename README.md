# Student Performance System

A simple website to manage student records and results. It is built with **Python (Flask)** and uses a small **SQLite** database.

Live website: https://student-performance-python.vercel.app

---

## What this project does

- Add, edit, search and delete students.
- Save marks for each subject (0 to 100).
- Automatically calculate **total**, **average** and **grade** for every student.
- Show a **dashboard** with class average, topper, grade counts and top 5 students.
- Show **reports**: student ranking, subject-wise results and department-wise results.
- Check that the app and database are working on the **status** page.

---

## Subjects

Mathematics, Physics, Chemistry, English, Computer Science

---

## Rules used

| Rule | Value |
|------|-------|
| Pass mark in each subject | 40 |
| Minimum attendance | 75% |

**Grade (based on average marks)**

| Average | Grade |
|---------|-------|
| 90 and above | A+ |
| 80 to 89 | A |
| 70 to 79 | B |
| 60 to 69 | C |
| 50 to 59 | D |
| Below 50 | F |

**Status of a student**

- **FAIL**: marks in any one subject are below 40.
- **AT RISK**: all subjects are passed, but attendance is below 75%.
- **PASS**: all subjects are passed and attendance is 75% or more.
- **NO DATA**: no marks have been added yet.

---

## Technologies used

- Python 3
- Flask
- SQLite
- HTML, CSS and JavaScript
- Git and GitHub
- Vercel (for hosting)

---

## Project files

| File | Purpose |
|------|---------|
| `app.py` | Main Python code (database, rules and all pages) |
| `base.html` | Common layout used by all pages |
| `dashboard.html` | Dashboard page |
| `students.html` | List of students with search and filter |
| `student_detail.html` | One student's marks and result |
| `student_form.html` | Form to add or edit a student |
| `reports.html` | Ranking and report page |
| `status.html` | App and database status page |
| `error.html` | Page shown when something is not found (404) |
| `style.css` | Design and colours |
| `app.js` | Small JavaScript for the pages |
| `requirements.txt` | Python packages needed |
| `Procfile` | Start command for hosting |
| `students.db` | SQLite database file |

---

## How to run it on your computer

1. Install Python 3.
2. Open the project folder in a terminal.
3. Install the packages:

   ```
   pip install -r requirements.txt
   ```

4. Start the app:

   ```
   python app.py
   ```

5. Open your browser and go to:

   ```
   http://localhost:5000
   ```

When the app starts for the first time, it creates the database and adds 8 sample students automatically.

---

## Main pages

| Page | Link |
|------|------|
| Dashboard | `/` |
| All students | `/students` |
| Add a student | `/students/new` |
| Reports | `/reports` |
| Status | `/status` |
| Health check | `/health` |

---

## Good things about the project

- Input is checked before saving (roll number, email, attendance and marks).
- Two students cannot have the same roll number.
- Deleting a student also deletes their marks.
- Safe database queries are used to avoid SQL injection.

---

## Limitations

- There is no login, so anyone with the link can change data.
- The sample data is for demonstration only and is not real student data.
- SQLite is good for small projects, not for very large use.

---

## Future ideas

- Login for teachers and admin.
- Import and export marks using Excel or CSV.
- Charts and graphs.
- Email alerts for students who are at risk.

---

## Author

**Shubham Manhas**
UID: 26MCI10131
MCA (AI&ML), Chandigarh University
