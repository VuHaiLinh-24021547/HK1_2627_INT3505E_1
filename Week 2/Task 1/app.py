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

_next_id = 1

@app.get("/books")
def list_books():
    return jsonify({
        "data": BOOKS,
        "total": len(BOOKS)}), 200

@app.post("/books")
def create_book(): 
    global _next_id

    if not request.is_json:
        return jsonify(error="expected JSON"), 415

    p = request.get_json(silent=True) or {}
    t = p.get("title", "").strip()
    a = p.get("author", "").strip()

    if not t or not a:
        return jsonify(error="required title and author"), 422

    book = {"id": _next_id,
            "title": t,
            "author": a}

    BOOKS.append(book)

    _next_id += 1

    resp = make_response(jsonify(book))
    resp.headers["Location"] = f"/books/{book.get('id')}"

    return resp

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)