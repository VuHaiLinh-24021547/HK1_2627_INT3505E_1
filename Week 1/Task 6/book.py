from flask import Flask, jsonify, request

app = Flask(__name__)
_next = 1
BOOKS = [{"id": 1, 
          "title": "Clean Code", 
          "author": "R. Martin",
          "year": 2001},
        {"id": 2,
         "title": "title4",
         "author": "author2",
         "year": 2000},
        {"id": 3,
         "title": "title3",
         "author": "test",
         "year": 2026}
        ]

def find(bid):
    return next((b for b in BOOKS if b["id"]==bid), None)

@app.route("/books", methods=["GET"])
def list_books():
    q = request.args.get("q", "").strip().lower()
    sort_by = request.args.get("sort", "").strip().lower()
    limit = int(request.args.get("limit", 100))

    results = BOOKS

    if q:
        results = [
            b for b in results 
            if q in b["title"].lower() or q in b["author"].lower()
        ]

    if sort_by in ["title", "author", "year", "id"]:
        results = sorted(results, key=lambda x: x.get(sort_by, ""))

    return jsonify(results[:limit]), 200

@app.route("/books/<int:bid>", methods=["GET"])
def get_book(bid):
    book = find(bid)

    if not book:
        return {"error":"not found"}, 404

    return jsonify(book), 200

@app.route("/books", methods=["POST"])
def create_book():
    global _next

    body = request.get_json(silent=True) or {}
    t, a, y = body.get("title"), body.get("author")

    if not t or not a:
        return {"error":"need title + author + year"}, 400

    if not y or type(y) is not int or y < 1900:
        return jsonify({"error": "need year > 1900"}), 400

    book = {"id": _next, 
            "title": t,
            "author": a,
            "year": y
    }

    _next += 1

    BOOKS.append(book)

    return jsonify(book), 201, {"Location":f"/books/{book['id']}"}

@app.route("/books/<int:bid>", methods=["PUT", "DELETE"])
def modify_book(bid):
    book = find(bid)

    if not book:
        return {"error":"not found"}, 404

    if request.method == "PUT":
        book.update(request.get_json(silent=True) or {})
        return jsonify(book), 200

    BOOKS.remove(book)

    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)