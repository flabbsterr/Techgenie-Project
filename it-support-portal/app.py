from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

def get_db():
    conn = sqlite3.connect("tickets.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("log_ticket"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        
        if user and user['password'] == password:
            session["username"] = username
            return redirect(url_for("log_ticket"))
        else:
            return render_template("login.html", error="Invalid credentials", username=username)
    
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        confirm_password = request.form["confirm_password"].strip()
        
        if not username or not password:
            return render_template("signup.html", error="Username and password are required")
        
        if password != confirm_password:
            return render_template("signup.html", error="Passwords do not match")
        
        # Validate password: 6+ characters and at least one number
        if len(password) < 6:
            return render_template("signup.html", error="Password must be at least 6 characters long")
        
        if not any(char.isdigit() for char in password):
            return render_template("signup.html", error="Password must contain at least one number")
        
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
            session["username"] = username
            return redirect(url_for("log_ticket"))
        except sqlite3.IntegrityError:
            return render_template("signup.html", error="Username already exists")
    
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/log", methods=["GET", "POST"])
def log_ticket():
    if "username" not in session:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        name = request.form["name"].strip()
        issue = request.form["issue"].strip()

        if name and issue:
            db = get_db()
            db.execute(
                "INSERT INTO tickets (name, issue, status, priority) VALUES (?, ?, ?, ?)",
                (name, issue, "Open", "Medium")
            )
            db.commit()

        return redirect(url_for("staff_tickets"))

    return render_template("log_ticket.html")

@app.route("/my-tickets")
def staff_tickets():
    if "username" not in session:
        return redirect(url_for("login"))
    
    db = get_db()
    tickets = db.execute("SELECT * FROM tickets").fetchall()
    return render_template("staff_tickets.html", tickets=tickets)

@app.route("/it", methods=["GET", "POST"])
def it_dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    
    db = get_db()

    if request.method == "POST":
        ticket_id = request.form["ticket_id"]
        status = request.form["status"]
        priority = request.form["priority"]

        db.execute(
            "UPDATE tickets SET status = ?, priority = ? WHERE id = ?",
            (status, priority, ticket_id)
        )
        db.commit()

    tickets = db.execute("SELECT * FROM tickets").fetchall()
    open_count = db.execute(
        "SELECT COUNT(*) FROM tickets WHERE status = 'Open'"
    ).fetchone()[0]

    return render_template("it_dashboard.html", tickets=tickets, open_count=open_count)

if __name__ == "__main__":
    app.run(debug=True)
