from flask import Flask, render_template, request, redirect, session
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "vinatha_secret_key"

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Create database
def init_db():
    conn = sqlite3.connect("letters.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS letters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            letter_text TEXT,
            file_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Users
users = {
    "smiruthi": "love123",
    "ajay": "star123",
    "Venkateswaran": "moon123",
    "Vijayalakshmi": "rose123",
    "Vidya": "wish123",
    "Bharathan": "cake123",
    "Parthasarathy": "gift123",
    "Kannammal": "hug123",
    "VINATHA": "queen123"
}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["user"] = username

            if username == "VINATHA":
                return redirect("/admin")
            return redirect("/submit")

    return render_template("login.html")

@app.route("/submit", methods=["GET", "POST"])
def submit():
    if "user" not in session or session["user"] == "VINATHA":
        return redirect("/login")

    if request.method == "POST":
        letter_text = request.form.get("letter_text")
        file = request.files.get("file")

        file_path = ""
        if file and file.filename != "":
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

        conn = sqlite3.connect("letters.db")
        c = conn.cursor()
        c.execute("INSERT INTO letters (username, letter_text, file_path) VALUES (?, ?, ?)",
                  (session["user"], letter_text, file_path))
        conn.commit()
        conn.close()

        return "Submitted successfully ❤️"

    return render_template("submit.html")

@app.route("/admin")
def admin():
    if "user" not in session or session["user"] != "VINATHA":
        return redirect("/login")

    conn = sqlite3.connect("letters.db")
    c = conn.cursor()
    c.execute("SELECT username, letter_text, file_path FROM letters")
    data = c.fetchall()
    conn.close()

    return render_template("admin.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)