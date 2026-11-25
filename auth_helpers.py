from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db

def create_account(name, email, password, role):
    with get_db() as db:
        db.execute("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)",
                   (name.strip(), email.strip().lower(), generate_password_hash(password), role))

def verify_account(email, password, role):
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE email=? AND role=?",
                          (email.strip().lower(), role)).fetchone()
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None
