from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlite3 import IntegrityError
from db import init_db, get_db
from auth_helpers import create_account, verify_account

app = Flask(__name__, template_folder="patient_templates", static_folder="static")
app.secret_key = "replace-with-a-long-random-patient-secret"
app.config["SESSION_COOKIE_NAME"] = "mim_patient_session"
init_db()

def patient_only():
    return session.get("role") == "patient"

@app.route("/")
def home():
    if patient_only():
        return redirect(url_for("dashboard"))
    return render_template("home.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        try:
            create_account(request.form["name"], request.form["email"], request.form["password"], "patient")
            flash("Your patient account is ready. Please log in.", "success")
            return redirect(url_for("login"))
        except IntegrityError:
            flash("This email is already registered.", "error")
    return render_template("auth.html", mode="Register", portal="Patient")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = verify_account(request.form["email"], request.form["password"], "patient")
        if user:
            session.clear()
            session.update(user_id=user["id"], name=user["name"], role="patient")
            return redirect(url_for("dashboard"))
        flash("Incorrect patient login details.", "error")
    return render_template("auth.html", mode="Login", portal="Patient")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if not patient_only():
        return redirect(url_for("login"))
    with get_db() as db:
        requests = db.execute("SELECT * FROM requests WHERE patient_id=? ORDER BY id DESC",
                              (session["user_id"],)).fetchall()
        responses = db.execute("""SELECT r.*, u.name AS shop_name FROM responses r
                                  JOIN users u ON u.id=r.shop_id
                                  JOIN requests q ON q.id=r.request_id
                                  WHERE q.patient_id=? ORDER BY r.id DESC""",
                               (session["user_id"],)).fetchall()
    return render_template("dashboard.html", requests=requests, responses=responses)

@app.route("/submit-request", methods=["POST"])
def submit_request():
    if not patient_only():
        return redirect(url_for("login"))
    description = request.form.get("description", "").strip()
    if len(description) < 10:
        flash("Please describe the problem in at least 10 characters.", "error")
    else:
        with get_db() as db:
            db.execute("INSERT INTO requests(patient_id,description) VALUES(?,?)",
                       (session["user_id"], description))
        flash("Your problem description has been shared with registered shops.", "success")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
