import hashlib
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

BOOKS = [
    {"id": 101, "title": "Book A", "author": "author 1"},
    {"id": 102, "title": "Book B", "author": "author 2"},
    {"id": 103, "title": "Book C", "author": "author 3"},
    {"id": 104, "title": "Book D", "author": "author 4"},
    {"id": 105, "title": "Book E", "author": "author 5"},
    {"id": 106, "title": "Book F", "author": "author 6"}
]

def generate_etag(book):
    content = f"{book['id']}:{book['title']}:{book['author']}".encode("utf-8")
    return f'"{hashlib.md5(content).hexdigest()[:12]}"'

@app.get("/books")
def list_books():
    return jsonify(BOOKS), 200

@app.get("/books/<int:bid>")
def get_book(bid):
    book = next((b for b in BOOKS if b["id"] == bid), None)
    if not book:
        return jsonify(error="not found"), 404

    etag = generate_etag(book)
    client_etag = request.headers.get("If-None-Match")

    if client_etag and client_etag == etag:
        resp = make_response("", 304)
        resp.headers["ETag"] = etag
        return resp

    resp = make_response(jsonify(book), 200)
    resp.headers["ETag"] = etag
    return resp

@app.patch("/books/<int:bid>")
def patch(bid):
    i = next((k for k,b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None:
        return jsonify(error="not found"), 404

    p = request.get_json(silent=True) or {}
    for k in "title author".split():
        if k in p:
            BOOKS[i][k] = p[k]

    return jsonify(BOOKS[i]), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)