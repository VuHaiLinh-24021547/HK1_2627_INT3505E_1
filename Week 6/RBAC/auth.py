import os
import sqlite3
import bcrypt
from functools import wraps
from flask import Flask, request, jsonify, g
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, 
    get_jwt_identity, get_jwt, verify_jwt_in_request
)

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "super-secret-key-123"
jwt = JWTManager(app)

DATABASE = "app_rbac.db"

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

class DBWrapper:
    def fetchone(self, query, params=()):
        cursor = get_db().execute(query, params)
        return cursor.fetchone()

db = DBWrapper()

def init_db():
    with app.app_context():
        conn = get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                pwd_hash BLOB,
                roles TEXT,
                scopes TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER,
                item_name TEXT
            )
        """)

        hashed_pwd = bcrypt.hashpw(b"password123", bcrypt.gensalt())
        
        conn.execute("""
            INSERT OR IGNORE INTO users (id, email, pwd_hash, roles, scopes) 
            VALUES (1, 'userA@test.com', ?, 'user', 'orders:read')
        """, (hashed_pwd,))

        conn.execute("""
            INSERT OR IGNORE INTO users (id, email, pwd_hash, roles, scopes) 
            VALUES (2, 'managerB@test.com', ?, 'manager', 'orders:read,orders:write')
        """, (hashed_pwd,))

        conn.execute("INSERT OR IGNORE INTO orders (id, owner_id, item_name) VALUES (100, 1, 'Laptop Dell')")
        conn.execute("INSERT OR IGNORE INTO orders (id, owner_id, item_name) VALUES (101, 2, 'Laptop Acer')")
        conn.commit()

@app.before_request
def load_current_user_middleware():
    g.current_user = None
    try:
        verify_jwt_in_request(optional=True)
        uid = get_jwt_identity()
        if uid:
            user_row = db.fetchone("SELECT id, email, roles FROM users WHERE id=?", (uid,))
            if user_row:
                g.current_user = {
                    "id": user_row["id"],
                    "email": user_row["email"],
                    "roles": user_row["roles"].split(",") if user_row["roles"] else []
                }
    except Exception:
        pass

def require_roles(*allowed):
    def d(fn):
        @wraps(fn)
        def w(*a, **kw):
            urs = set(g.current_user["roles"]) if g.current_user else set()
            if not urs & set(allowed):
                return jsonify({
                    "error": "forbidden",
                    "need_one_of": list(allowed)
                }), 403
            return fn(*a, **kw)
        return w
    return d

def require_scopes(*needed):
    def d(fn):
        @wraps(fn)
        def w(*a, **kw):
            granted = set(get_jwt().get("scopes", []))
            if not set(needed).issubset(granted):
                return jsonify({
                    "error": "insufficient_scope",
                    "need_all_of": list(needed)
                }), 403
            return fn(*a, **kw)
        return w
    return d

def user_owns_resource(param="id"):
    def d(fn):
        @wraps(fn)
        def w(*a, **kw):
            row = db.fetchone(
                "SELECT owner_id FROM orders WHERE id=?",
                (kw[param],)
            )
            if not row:
                return jsonify({"e": "nf"}), 404
            
            ok = str(row["owner_id"]) == str(g.current_user["id"])
            if not ok and "admin" not in g.current_user["roles"]:
                return jsonify({"error": "forbidden"}), 403
            
            return fn(*a, **kw)
        return w
    return d

class OrderService:
    def delete_authorized(self, order_id, current_user):
        conn = get_db()
        conn.execute("DELETE FROM orders WHERE id=?", (order_id,))
        conn.commit()

order_svc = OrderService()

@app.post("/api/login")
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password", "")
    
    if not email or not password:
        return jsonify({"error": "missing_email_or_password"}), 400

    user = db.fetchone("SELECT id, pwd_hash, roles, scopes FROM users WHERE email=?", (email,))

    pwd_bytes = password.encode("utf-8")
    stored_hash = user["pwd_hash"] if user else None
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode("utf-8")
        
    if not user or not bcrypt.checkpw(pwd_bytes, stored_hash):
        return jsonify({"error": "invalid_credentials"}), 401

    user_scopes = user["scopes"].split(",") if user["scopes"] else []

    access_token = create_access_token(
        identity=str(user["id"]),
        additional_claims={"scopes": user_scopes}
    )
    
    return jsonify(access_token=access_token), 200

@app.get("/api/orders/<int:id>")
@jwt_required()
@require_scopes("orders:read")
@user_owns_resource("id")
def get_order(id):
    order = db.fetchone("SELECT id, owner_id, item_name FROM orders WHERE id=?", (id,))
    
    return jsonify({
        "id": order["id"],
        "owner_id": order["owner_id"],
        "item_name": order["item_name"]
    }), 200

@app.delete("/api/orders/<int:id>")
@jwt_required()
@require_roles("admin", "manager")
@require_scopes("orders:write")
@user_owns_resource("id")
def delete_order(id):
    order_svc.delete_authorized(id, g.current_user)
    return "", 204

if __name__ == "__main__":
    init_db()
    app.run(debug=True)