import os
import sqlite3
from flask import Flask, request, jsonify, g
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
import bcrypt

app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "super-secret-key"),
    JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY", "super-jwt-secret"),
    JWT_ACCESS_TOKEN_EXPIRES=900,
    JWT_REFRESH_TOKEN_EXPIRES=2592000,
    JWT_ALGORITHM="HS256"
)

jwt = JWTManager(app)

DATABASE = 'app.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                pwd_hash BLOB
            )
        ''')
        hashed = bcrypt.hashpw(b"password123", bcrypt.gensalt())
        db.execute('INSERT OR IGNORE INTO users (email, pwd_hash) VALUES (?, ?)', 
                   ("admin@example.com", hashed))
        db.commit()

def load_permissions(user_id):
    return {"roles": ["admin"], "scopes": ["orders:read", "orders:write"]}

def orders_by_owner(uid):
    return {"orders": ["order-1", "order-2"], "owner": uid}

BLOCKLIST = set() 

@jwt.token_in_blocklist_loader
def check_revoked(_h, claims):
    jti = claims["jti"]
    return jti in BLOCKLIST

@app.post("/api/auth/logout")
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    BLOCKLIST.add(jti) 
    return jsonify(msg="Logged out successfully")

@app.post("/api/auth/login")
def login():
    email = request.json.get("email")
    pwd_input = request.json.get("password", "")
    
    db = get_db()
    user = db.execute("SELECT id, pwd_hash FROM users WHERE email=?", (email,)).fetchone()
    
    if not user or not bcrypt.checkpw(pwd_input.encode(), user["pwd_hash"]):
        return jsonify(error="invalid_credentials"), 401
    
    claims = load_permissions(user["id"])
    uid = str(user["id"])
    
    return jsonify(
        access=create_access_token(
            identity=uid, additional_claims=claims),
        refresh=create_refresh_token(
            identity=uid, additional_claims=claims)
    )

@app.get("/api/orders")
@jwt_required()
def list_orders():
    uid = get_jwt_identity()
    claims = get_jwt()
    
    if "orders:read" not in claims.get("scopes", []):
        return jsonify(error="insufficient_scope"), 403
        
    return jsonify(orders_by_owner(uid))

@app.post("/api/auth/refresh")
@jwt_required(refresh=True)
def refresh():
    claims = load_permissions(get_jwt_identity())
    
    return jsonify(
        access=create_access_token(
            identity=get_jwt_identity(), additional_claims=claims)
    )

if __name__ == "__main__":
    init_db() 
    app.run(debug=True)