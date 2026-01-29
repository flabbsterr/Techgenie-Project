from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# In-memory storage
users = {
    "staff": "password123",
    "it": "itadmin123"
}

tickets = [
    {"id": 1, "name": "John Doe", "issue": "Computer won't start", "status": "Open", "priority": "High"},
    {"id": 2, "name": "Jane Smith", "issue": "Email not working", "status": "In Progress", "priority": "Medium"},
    {"id": 3, "name": "Bob Johnson", "issue": "Printer offline", "status": "Closed", "priority": "Low"}
]
ticket_id_counter = 4

@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("log_ticket"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].replace(" ", "")
        password = request.form["password"]
        
        if username in users and users[username] == password:
            session["username"] = username
            return redirect(url_for("log_ticket"))
        else:
            return render_template("login.html", error="Invalid credentials", username=username)
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/log", methods=["GET", "POST"])
def log_ticket():
    global ticket_id_counter
    
    if "username" not in session:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        name = request.form["name"].strip()
        issue = request.form["issue"].strip()

        if name and issue:
            ticket = {
                "id": ticket_id_counter,
                "name": name,
                "issue": issue,
                "status": "Open",
                "priority": "Medium"
            }
            tickets.append(ticket)
            ticket_id_counter += 1

        return redirect(url_for("staff_tickets"))

    return render_template("log_ticket.html")

@app.route("/my-tickets")
def staff_tickets():
    if "username" not in session:
        return redirect(url_for("login"))
    
    return render_template("staff_tickets.html", tickets=tickets)

@app.route("/it", methods=["GET", "POST"])
def it_dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        ticket_id = int(request.form["ticket_id"])
        status = request.form["status"]
        priority = request.form["priority"]

        for ticket in tickets:
            if ticket["id"] == ticket_id:
                ticket["status"] = status
                ticket["priority"] = priority
                break

    open_count = sum(1 for ticket in tickets if ticket["status"] == "Open")
    closed_count = sum(1 for ticket in tickets if ticket["status"] == "Closed")
    return render_template("it_dashboard.html", tickets=tickets, open_count=open_count, closed_count=closed_count)

@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("login"))
    
    username = session["username"]
    user_tickets = [t for t in tickets if t["name"].lower() == username.lower()]
    open_tickets = sum(1 for t in user_tickets if t["status"] == "Open")
    closed_tickets = sum(1 for t in user_tickets if t["status"] == "Closed")
    
    return render_template("profile.html", user_tickets=user_tickets, 
                         open_tickets=open_tickets, closed_tickets=closed_tickets)

if __name__ == "__main__":
    app.run(debug=True, port=5000)