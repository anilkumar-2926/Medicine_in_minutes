from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlite3 import IntegrityError
from db import init_db, get_db
from auth_helpers import create_account, verify_account

app = Flask(__name__, template_folder="shop_templates", static_folder="static")
app.secret_key = "replace-with-a-long-random-shop-secret"
app.config["SESSION_COOKIE_NAME"] = "mim_shop_session"
init_db()

def shop_only():
    return session.get("role") == "shop"

@app.route("/")
def home():
    if shop_only():
        return redirect(url_for("dashboard"))
    return render_template("home.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        try:
            create_account(request.form["name"], request.form["email"], request.form["password"], "shop")
            flash("Shop account created. Please log in.", "success")
            return redirect(url_for("login"))
        except IntegrityError:
            flash("This email is already registered.", "error")
    return render_template("auth.html", mode="Register", portal="Medical Shop")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = verify_account(request.form["email"], request.form["password"], "shop")
        if user:
            session.clear()
            session.update(user_id=user["id"], name=user["name"], role="shop")
            return redirect(url_for("dashboard"))
        flash("Incorrect shop login details.", "error")
    return render_template("auth.html", mode="Login", portal="Medical Shop")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if not shop_only():
        return redirect(url_for("login"))
    with get_db() as db:
        requests = db.execute("""SELECT q.*, u.name AS patient_name FROM requests q
                                 JOIN users u ON u.id=q.patient_id
                                 WHERE NOT EXISTS (
                                   SELECT 1 FROM responses r WHERE r.request_id=q.id AND r.shop_id=?
                                 ) ORDER BY q.id DESC""", (session["user_id"],)).fetchall()
        mine = db.execute("""SELECT r.*, q.description, u.name AS patient_name
                             FROM responses r JOIN requests q ON q.id=r.request_id
                             JOIN users u ON u.id=q.patient_id
                             WHERE r.shop_id=? ORDER BY r.id DESC""",
                          (session["user_id"],)).fetchall()
    return render_template("dashboard.html", requests=requests, mine=mine)

@app.route("/respond/<int:request_id>", methods=["POST"])
def respond(request_id):
    if not shop_only():
        return redirect(url_for("login"))
    medicine = request.form.get("medicine_name", "").strip()
    message = request.form.get("message", "").strip()
    try:
        price = float(request.form.get("price", "0"))
        if not medicine or not message or price < 0:
            raise ValueError()
        with get_db() as db:
            exists = db.execute("SELECT id FROM requests WHERE id=?", (request_id,)).fetchone()
            if not exists:
                flash("Patient request not found.", "error")
            else:
                db.execute("""INSERT INTO responses(request_id,shop_id,medicine_name,price,message)
                              VALUES(?,?,?,?,?)""",
                           (request_id, session["user_id"], medicine, price, message))
                flash("Your response has been sent to the patient.", "success")
    except ValueError:
        flash("Enter a medicine name, valid price and response message.", "error")
    except IntegrityError:
        flash("You have already responded to this request.", "error")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
