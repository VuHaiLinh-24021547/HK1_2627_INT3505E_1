from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

BOOKS = [
    {"id": 101, "title": "Book A", "author": "Orwell", "isbn": "000-000-0-00000-0", "price": 5000},
    {"id": 102, "title": "Book B", "author": "author 2", "isbn": "000-000-0-00000-0", "price": 5000},
    {"id": 103, "title": "Book C", "author": "author 3", "isbn": "000-000-0-00000-0", "price": 5000},
    {"id": 104, "title": "Book D", "author": "author 4", "isbn": "000-000-0-00000-0", "price": 5000},
    {"id": 105, "title": "Book E", "author": "author 5", "isbn": "000-000-0-00000-0", "price": 5000},
    {"id": 106, "title": "clean F", "author": "author 6", "isbn": "000-000-0-00000-0", "price": 5000}
]

DEFAULT_SIZE, MAX_SIZE = 20, 100

@app.get("/books")
def list_books():
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", DEFAULT_SIZE))
    except ValueError:
        return jsonify(error="page and size must be int"), 400

    page = max(page, 1)
    size = max(min(size, MAX_SIZE), 1)

    flt = BOOKS

    a = request.args.get("author")
    if a:
        flt = [b for b in flt if b["author"].lower() == a.lower()]

    q = request.args.get("q")
    if q:
        flt = [b for b in flt if q in b["title"].lower()]

    total = len(flt)
    start = (page - 1) * size
    end = start + size
    item = flt[start:end]
    last = (total + size - 1) // size

    def u(p):
        return f"/books?page={p}&size={size}"

    links = {
        "self": {"herf": u(page)},
        "first": {"href": u(1)},
        "last": {"href": u(max(last, 1))}
    }

    if (page > 1):
        links["prev"] = {"href": u(page - 1)}
    if (end < total):
        links["next"] = {"href": u(page + 1)}

    body = {
        "data": item,
        "pagination": {"page": page, "size": size, "total": total, "total_pages": last},
        "_links": links
    }

    resp = make_response(jsonify(body), 200)
    resp.headers["Cache-Control"] = "public, max-age=30"

    return resp

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)    