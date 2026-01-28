from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("tickets.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return redirect(url_for("log_ticket"))

@app.route("/log", methods=["GET", "POST"])
def log_ticket():
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
    db = get_db()
    tickets = db.execute("SELECT * FROM tickets").fetchall()
    return render_template("staff_tickets.html", tickets=tickets)

@app.route("/it", methods=["GET", "POST"])
def it_dashboard():
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
