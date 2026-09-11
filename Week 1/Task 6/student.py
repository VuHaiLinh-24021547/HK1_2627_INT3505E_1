from flask import Flask, jsonify, request

app = Flask(__name__)
_next = 1
STUDENTS = [
    {
        "id":1,
        "name":"Steve",
        "gpa":3.4
    },
    {
        "id":2,
        "name":"An",
        "gpa":2.0
    },
    {
        "id":3,
        "name":"ching chong",
        "gpa":0.0
    }
]

def find(sid):
    return next((s for s in STUDENTS if s["id"] == sid), None)

@app.route("/students", methods=["GET"])
def list_students():
    n = int(request.args.get("limit", 100))
    return jsonify(STUDENTS[:n]), 200

@app.route("/students/<int:sid>", methods=["GET"])
def get_student(sid):
    student = STUDENTS[sid]

    if not student:
        return {"error":"not found"}, 404

    return jsonify(student), 200


@app.route("/students", methods=["POST"])
def create_student():
    global _next

    body = request.get_json(silent=True) or {}
    name, gpa = body.get("name"), body.get("gpa")

    if not name or not gpa:
        return {"error":"required name and gpa"}, 400

    student = {
        "id":_next,
        "name":name,
        "gpa":gpa
    }

    _next += 1
    STUDENTS.append(student)

    return jsonify(student), 201, {"Location":f"/students/{student['id']}"}

@app.route("/students/<int:sid>", methods=["PUT", "DELETE"])
def modify_student(sid):
    student = find(sid)

    if not student:
        return {"error":"not found"}, 404

    if request.method == "PUT":
        student.update(request.get_json(silent=True) or {})
        return jsonify(student), 200

    STUDENTS.remove(student)

    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)