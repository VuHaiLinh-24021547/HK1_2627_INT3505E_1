import sqlite3
import secrets
import hashlib
from datetime import datetime, timezone
from functools import wraps
from flask import Flask, request, jsonify, g

app = Flask(__name__)
DATABASE = 'api_keys.db'

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

def now_utc():
    return datetime.now(timezone.utc).isoformat()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prefix VARCHAR(16),
                hash VARCHAR(64) UNIQUE,
                last4 CHAR(4),
                owner_id INTEGER,
                scopes VARCHAR(128),
                created_at TIMESTAMP,
                expires_at TIMESTAMP NULL,
                revoked_at TIMESTAMP NULL,
                ip_allowlist TEXT
            )
        ''')
        db.commit()

def mint_key(prefix, owner_id, scopes):
    raw = secrets.token_urlsafe(32)
    digest = hashlib.sha256(raw.encode()).hexdigest()[:8]
    plain = f"{prefix}_{raw}_{digest}"
    hashed_store = hashlib.sha256(plain.encode()).hexdigest()
    
    with app.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO api_keys (prefix, hash, last4, owner_id, scopes, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (prefix, hashed_store, plain[-4:], owner_id, scopes, now_utc())
        )
        db.commit()
        
    return plain

def require_api_key(scopes=None):
    def d(fn):
        @wraps(fn)
        def w(*a, **kw):
            key = request.headers.get("X-Api-Key", "")
            if not key:
                return jsonify({"e": "missing key"}), 401
                
            hashed = hashlib.sha256(key.encode()).hexdigest()
            db = get_db()

            cursor = db.execute(
                "SELECT id, owner_id, scopes, revoked_at, expires_at "
                "FROM api_keys WHERE hash=?", (hashed,)
            )
            row = cursor.fetchone()

            if (not row or row["revoked_at"] or
                (row["expires_at"] is not None and
                 row["expires_at"] <= now_utc())):
                return jsonify({"e": "invalid or expired key"}), 401

            granted = set(row["scopes"].split(","))
            if scopes and not set(scopes).issubset(granted):
                return jsonify({"e": "insufficient scope"}), 403

            g.api_key_id = row["id"]
            g.owner_id = row["owner_id"]
            g.api_scopes = granted
            
            return fn(*a, **kw)
        return w
    return d

@app.route("/api/read-only", methods=["GET"])
@require_api_key(scopes=["read"])
def read_data():
    return jsonify({"message": "Read access granted", "owner_id": g.owner_id})

@app.route("/api/payments", methods=["POST"])
@require_api_key(scopes=["read", "write"])
def process_payment():
    return jsonify({"message": "Payment processed", "owner_id": g.owner_id})

if __name__ == "__main__":
    init_db()
    test_key = mint_key(prefix="sk_test", owner_id=101, scopes="read,write")
    print(f"Key: {test_key}")
    app.run(ssl_context="adhoc")