from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException
import uuid

ERROR_BASE = "https://api.example.com/errors"

class ProblemError(Exception):
    def __init__(self, status, title, detail=None, type_path=None, **extra):
        self.status = status
        self.title = title
        self.detail = detail
        self.type_path = f"{ERROR_BASE}/{type_path}" if type_path else "about:blank"

def _problem(status, title, detail=None, type_path=None, **extra):
    body = {
        "type": f"{ERROR_BASE}/{type_path}" if type_path else "about:blank",
        "title": title,
        "status": status,
        "instance": request.path,
        "trace_id": str(uuid.uuid4()),
    }

    if detail:
        body["detail"] = detail
    body.update(extra)

    resp = jsonify(body)
    resp.status_code = status
    resp.headers["Content-Type"] = "application/problem+json"

    return resp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }

with app.app_context():
    db.create_all()

@app.errorhandler(ProblemError)
def handle_problem_error(e):
    return _problem(e.status, e.title, e.detail, e.type_path)

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    return _problem(e.code, e.name, e.description)

@app.errorhandler(Exception)
def handle_unhandled_exception(e):
    app.logger.error("Unhandled Exception Exception occurred:", exc_info=e)

    return _problem(
        status=500,
        title="Internal Server Error",
        detail="System error."
    )

@app.get("/users/<int:id>")
def get_user(id):
    user = User.query.get(id)
    if not user:
        raise ProblemError(
            status= 404,
            title= "User not found",
            type_path= "user-not-found",
            resource_id = id,
        )
    return jsonify(user.to_dict())

@app.get("/crash")
def crash_test():
    result = 1 / 0  
    return jsonify({"result": result})

if (__name__ == "__main__"):
    app.run(host="127.0.0.1", port=5000, debug=True)
