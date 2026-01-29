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

@app.route("/signup", methods=["GET", "POST"])
def signup():
    global ticket_id_counter
    
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        confirm_password = request.form["confirm_password"].strip()
        
        if not username or not password:
            return render_template("signup.html", error="Username and password are required")
        
        if " " in username:
            return render_template("signup.html", error="Username cannot contain spaces")
        
        if password != confirm_password:
            return render_template("signup.html", error="Passwords do not match")
        
        # Validate password: 6+ characters and at least one number
        if len(password) < 6:
            return render_template("signup.html", error="Password must be at least 6 characters long")
        
        if not any(char.isdigit() for char in password):
            return render_template("signup.html", error="Password must contain at least one number")
        
        if username in users:
            return render_template("signup.html", error="Username already exists")
        
        users[username] = password
        session["username"] = username
        return redirect(url_for("log_ticket"))
    
    return render_template("signup.html")

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

@app.route("/change-password", methods=["POST"])
def change_password():
    if "username" not in session:
        return redirect(url_for("login"))
    
    username = session["username"]
    current_password = request.form["current_password"]
    new_password = request.form["new_password"]
    confirm_password = request.form["confirm_password"]
    
    if users[username] != current_password:
        user_tickets = [t for t in tickets if t["name"].lower() == username.lower()]
        open_tickets = sum(1 for t in user_tickets if t["status"] == "Open")
        closed_tickets = sum(1 for t in user_tickets if t["status"] == "Closed")
        return render_template("profile.html", error="Current password is incorrect",
                             user_tickets=user_tickets, open_tickets=open_tickets, closed_tickets=closed_tickets)
    
    if new_password != confirm_password:
        user_tickets = [t for t in tickets if t["name"].lower() == username.lower()]
        open_tickets = sum(1 for t in user_tickets if t["status"] == "Open")
        closed_tickets = sum(1 for t in user_tickets if t["status"] == "Closed")
        return render_template("profile.html", error="New passwords do not match",
                             user_tickets=user_tickets, open_tickets=open_tickets, closed_tickets=closed_tickets)
    
    if len(new_password) < 6 or not any(char.isdigit() for char in new_password):
        user_tickets = [t for t in tickets if t["name"].lower() == username.lower()]
        open_tickets = sum(1 for t in user_tickets if t["status"] == "Open")
        closed_tickets = sum(1 for t in user_tickets if t["status"] == "Closed")
        return render_template("profile.html", error="Password must be at least 6 characters with one number",
                             user_tickets=user_tickets, open_tickets=open_tickets, closed_tickets=closed_tickets)
    
    users[username] = new_password
    return redirect(url_for("profile"))

@app.route("/delete-account")
def delete_account():
    if "username" not in session:
        return redirect(url_for("login"))
    
    username = session["username"]
    if username in users:
        del users[username]
    
    session.pop("username", None)
    return redirect(url_for("login"))

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

if __name__ == "__main__":
    app.run(debug=True)
