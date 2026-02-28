from flask import Flask, render_template, request, redirect, session, send_from_directory
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ===============================
# DATABASE SETUP
# ===============================
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            message TEXT,
            filename TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ===============================
# USERS
# ===============================
users = {
    "smiruthi": "smile1",
    "ajay": "ajay123",
    "Venkateswaran": "venky7",
    "Vijayalakshmi": "viji9",
    "Vidya": "vidya5",
    "Bharathan": "bharat8",
    "Parthasarathy": "partha4",
    "Kannammal": "kanna6",
    "vinatha": "queenmom"   # ADMIN 👑
}

# ===============================
# HOME
# ===============================
@app.route("/")
def home():
    return render_template("home.html")

# ===============================
# LOGIN
# ===============================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["username"] = username

            if username == "vinatha":
                return redirect("/admin")
            else:
                return redirect("/submit")
        else:
            return "Invalid Login"

    return render_template("login.html")

# ===============================
# SUBMIT / EDIT
# ===============================
@app.route("/submit", methods=["GET", "POST"])
def submit():
    if "username" not in session:
        return redirect("/login")

    if session["username"] == "vinatha":
        return redirect("/admin")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":
        message = request.form["message"]
        file = request.files["file"]
        filename = None

        if file and file.filename != "":
            filename = file.filename
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        # Check if user already submitted
        c.execute("SELECT * FROM entries WHERE username=?", (session["username"],))
        existing = c.fetchone()

        if existing:
            c.execute(
                "UPDATE entries SET message=?, filename=? WHERE username=?",
                (message, filename, session["username"])
            )
        else:
            c.execute(
                "INSERT INTO entries (username, message, filename) VALUES (?, ?, ?)",
                (session["username"], message, filename)
            )

        conn.commit()

    # Fetch current user's entry
    c.execute("SELECT * FROM entries WHERE username=?", (session["username"],))
    entry = c.fetchone()
    conn.close()

    return render_template("submit.html", entry=entry)

# ===============================
# DELETE
# ===============================
@app.route("/delete", methods=["POST"])
def delete():
    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM entries WHERE username=?", (session["username"],))
    conn.commit()
    conn.close()

    return redirect("/submit")

# ===============================
# ADMIN DASHBOARD
# ===============================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "username" not in session or session["username"] != "vinatha":
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT id, username FROM entries")
    entries = c.fetchall()

    selected = None

    if request.method == "POST":
        entry_id = request.form["id"]
        c.execute("SELECT * FROM entries WHERE id=?", (entry_id,))
        selected = c.fetchone()

    conn.close()

    return render_template("admin.html", entries=entries, selected=selected)

# ===============================
# SERVE UPLOADED FILES
# ===============================
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ===============================
# LOGOUT
# ===============================
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/")

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    app.run(debug=True)