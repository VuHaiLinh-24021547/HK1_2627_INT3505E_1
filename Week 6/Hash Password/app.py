import sqlite3
from flask import Flask, request, jsonify, g
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity


from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError, InvalidHashError

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret-jwt-key"
jwt = JWTManager(app)

DATABASE = "app_argon2.db"

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    type=Type.ID
)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                pwd_hash TEXT
            )
        """)
        db.commit()


@app.post("/api/register")
def register():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "missing_fields"}), 400

    pwd_hash = ph.hash(password)

    db = get_db()
    try:
        db.execute("INSERT INTO users (email, pwd_hash) VALUES (?, ?)", (email, pwd_hash))
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "email_already_exists"}), 400

    return jsonify({"message": "registered_successfully"}), 201

@app.post("/api/login")
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "missing_credentials"}), 400

    db = get_db()
    user = db.execute("SELECT id, pwd_hash FROM users WHERE email=?", (email,)).fetchone()

    if not user:
        return jsonify({"error": "invalid_credentials"}), 401

    stored = user["pwd_hash"]

    try:
        ph.verify(stored, password)
    except (VerifyMismatchError, InvalidHashError):
        return jsonify({"error": "invalid_credentials"}), 401
    else:
        if ph.check_needs_rehash(stored):
            new_hash = ph.hash(password)
            db.execute("UPDATE users SET pwd_hash=? WHERE id=?", (new_hash, user["id"]))
            db.commit()

        access_token = create_access_token(identity=str(user["id"]))
        return jsonify(access_token=access_token), 200

@app.get("/api/me")
@jwt_required()
def me():
    uid = get_jwt_identity()
    return jsonify({"user_id": uid}), 200

if __name__ == "__main__":
    init_db()
    app.run(debug=True)