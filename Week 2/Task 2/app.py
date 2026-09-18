from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

BOOKS = [
    {"id": 101, "title": "Book A", "author": "author 1", "isbn": "000-000-0-00000-0", "price": 5000},
    {"id": 102, "title": "Book B", "author": "author 2", "isbn": "000-000-0-00000-0", "price": 5000},
    {"id": 103, "title": "Book C", "author": "author 3", "isbn": "000-000-0-00000-0", "price": 5000},
    {"id": 104, "title": "Book D", "author": "author 4", "isbn": "000-000-0-00000-0", "price": 5000},
    {"id": 105, "title": "Book E", "author": "author 5", "isbn": "000-000-0-00000-0", "price": 5000},
    {"id": 106, "title": "Book F", "author": "author 6", "isbn": "000-000-0-00000-0", "price": 5000}
]

@app.get("/books/<int:bid>")
def fetch(bid):
    i = next((k for k,b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None:
        return jsonify(error="not found"), 404

    resp = make_response(jsonify(BOOKS[i]), 200)
    resp.headers["Cache-Control"] = "max-age=60"

    return resp

@app.put("/books/<int:bid>")
def put(bid):
    i = next((k for k,b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None:
        return jsonify(error="not found"), 404

    p = request.get_json(silent=True) or {}
    t, a = p.get("title"), p.get("author")

    if not t or not a:
        return jsonify(error="required title and author"), 422

    BOOKS[i] = {
        "id": bid,
        "title": t.strip(),
        "author": a.strip(),
        "isbn": p.get("isbn"),
        "price": p.get("price")
    }

    return jsonify(BOOKS[i]), 200

@app.patch("/books/<int:bid>")
def patch(bid):
    i = next((k for k,b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None:
        return jsonify(error="not found"), 404

    p = request.get_json(silent=True) or {}
    if (p.get("price") < 0):
        return jsonify(error="price must be positive"), 422
    for k in "title author isbn price".split():
        if k in p:
            BOOKS[i][k] = p[k]

    return jsonify(BOOKS[i]), 200

@app.delete("/books/<int:bid>")
def delete(bid):
    i = next((k for k,b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None:
        return jsonify(error="not found"), 404

    BOOKS.pop(i)

    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)