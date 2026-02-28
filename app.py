from flask import Flask, render_template, request, redirect, session
import os
import psycopg2
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    url = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    return conn

# ================= USERS =================
users = {
    "smiruthi": "smile1",
    "ajay": "ajay123",
    "Venkateswaran": "venky7",
    "Vijayalakshmi": "viji9",
    "Vidya": "vidya5",
    "Bharathan": "bharat8",
    "Parthasarathy": "partha4",
    "Kannammal": "kanna6",
    "vinatha": "queenmom"
}

# ================= INIT TABLE =================
def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            message TEXT,
            filename TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

# ================= HOME =================
@app.route("/")
def home():
    return render_template("home.html")

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if u in users and users[u] == p:
            session["username"] = u
            if u == "vinatha":
                return redirect("/admin")
            return redirect("/submit")
        return "Invalid Login"

    return render_template("login.html")

# ================= SUBMIT =================
@app.route("/submit", methods=["GET", "POST"])
def submit():
    if "username" not in session:
        return redirect("/login")

    if session["username"] == "vinatha":
        return redirect("/admin")

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        msg = request.form["message"]

        cur.execute("""
            INSERT INTO entries (username, message)
            VALUES (%s, %s)
            ON CONFLICT (username)
            DO UPDATE SET message = EXCLUDED.message
        """, (session["username"], msg))

        conn.commit()

    cur.execute("SELECT * FROM entries WHERE username=%s", (session["username"],))
    entry = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("submit.html", entry=entry)

# ================= DELETE =================
@app.route("/delete", methods=["POST"])
def delete():
    if "username" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM entries WHERE username=%s", (session["username"],))
    conn.commit()
    cur.close()
    conn.close()

    return redirect("/submit")

# ================= ADMIN =================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "username" not in session or session["username"] != "vinatha":
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    # Fetch full data including id
    cur.execute("SELECT id, username, message FROM entries")
    rows = cur.fetchall()

    # Convert tuples to dictionaries
    entries = []
    for row in rows:
        entries.append({
            "id": row[0],
            "username": row[1],
            "message": row[2]
        })

    selected = None

    if request.method == "POST":
        entry_id = request.form["id"]
        for entry in entries:
            if str(entry["id"]) == entry_id:
                selected = entry
                break

    cur.close()
    conn.close()

    return render_template("admin.html", entries=entries, selected=selected)
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)