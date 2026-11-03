from flask import Blueprint, jsonify
from sqlalchemy import text
from extensions import db

health_bp = Blueprint("health", __name__, url_prefix="")

# Liveness probe: Kiểm tra process service còn sống (không check DB)
@health_bp.get("/healthz")
def liveness():
    return jsonify({"status": "ok"}), 200

# Readiness probe: Kiểm tra kết nối tới cơ sở dữ liệu
@health_bp.get("/ready")
def readiness():
    checks = {}
    try:
        db.session.execute(text("SELECT 1"))
        checks["db"] = "ok"
    except Exception:
        checks["db"] = "err"

    ok = all(v == "ok" for v in checks.values())
    return jsonify({
        "status": "ok" if ok else "degraded",
        "checks": checks
    }), 200 if ok else 503