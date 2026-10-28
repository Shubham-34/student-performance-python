# Student Performance System (Python)

A working website built with **Python + Flask + SQLite**. Open it in Chrome; edit the code in Visual Studio Code.

```
Chrome (HTML pages)  ──HTTP──▶  Flask (app.py)  ──▶  sqlite3  ──▶  data/students.db
```

## Features

- Add, edit, delete and search students (filter by department)
- Add, update and remove marks per subject
- Average, total, grade and status (PASS / FAIL / AT RISK for attendance below 75%)
- Dashboard with class statistics and top performer
- Reports: leaderboard, per-subject and per-department statistics (SQL `JOIN` / `GROUP BY`)
- DB status page showing the live database connection and row counts
- Interactive interface: live search and department filter, click-to-sort columns, animated numbers and charts (results donut, grade distribution, score bars), light / dark theme button, pop-up delete confirmation, slider and subject buttons for entering marks, notification toasts
- 8 demo students are added the first time you run it

## Run it in Visual Studio Code

1. Install **Python 3.10 or newer** from python.org (tick "Add Python to PATH") and **VS Code** with the **Python** extension.
2. Extract the zip. In VS Code: `File > Open Folder…` and choose the `student-performance-python` folder.
3. Open the terminal in VS Code (`Ctrl+` `` ` ``) and run:

   ```
   python -m venv .venv
   .venv\Scripts\activate          (Windows)    source .venv/bin/activate   (Mac / Linux)
   pip install -r requirements.txt
   python app.py
   ```

4. Open **http://localhost:5000** in Chrome. Stop the server with `Ctrl+C`.

The database file is created automatically in the `data/` folder. To start with fresh demo data, stop the server and delete `data/`.

## Put it on the internet

Any Python host works (Render, Railway, PythonAnywhere…). On Render or Railway:

1. Push this folder to a GitHub repository.
2. Create a **Web Service** from the repo.
   Build command: `pip install -r requirements.txt`
   Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
3. Set the environment variable `SECRET_KEY` to a long random string.
4. Open the public URL.

SQLite stores data in a file, and many free hosts wipe the disk on redeploy. For a demo that is fine; for data you want to keep, attach a persistent disk and set `DB_PATH` to a path on it.

## Files

```
app.py                 routes, SQL, grading rules
templates/             HTML pages (Jinja)
static/style.css       styling (light + dark theme)
static/app.js          interactivity (search, sort, charts, dialogs)
requirements.txt       Flask, gunicorn
Procfile               start command for hosting
.vscode/tasks.json     Ctrl+Shift+B runs the site
```
