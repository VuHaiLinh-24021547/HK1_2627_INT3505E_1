from flask import Blueprint, request, jsonify
from jsonschema import validate, ValidationError
import json
import base64
from sqlalchemy import select, tuple_
from models import db, Book, Author

bp = Blueprint('books', __name__)
SCHEMA = json.load(open("./schemas/book.json"))

SORT = {"id": Book.id, "price": Book.price_vnd}

def parse_sort(raw):
    desc = raw.startswith("-")
    key = raw.lstrip("-")

    if key not in SORT:
        return None, "bad_sort", 400

    p = SORT[key]
    cols = [
        p.desc() if desc else p.asc(),
        Book.id.desc() if desc else Book.id.asc()
    ]

    return p, cols, desc

def _enc(s):
    return base64.urlsafe_b64encode(
        json.dumps(s).encode()
    ).decode().rstrip("=")

def apply_cursor(q, raw, sort, p, desc):
    if not raw:
        return q, None, 200

    pad = "=" * (-len(raw) % 4)
    c = json.loads(
        base64.urlsafe_b64decode(raw + pad)
    )

    if c.get("s") != sort:
        return None, "sort_chg", 400

    v, i = c["v"], c["i"]
    op = "<" if desc else ">"

    condition = tuple_(p, Book.id).op(op)((v, i))

    return q.filter(condition), None, 200

def build_response(items, lim, sort, p, more):
    nxt = None
    if items and more:
        last = items[-1]
        nxt = _enc({
            "s": sort,
            "v": getattr(last, p.key),
            "i": last.id
        })
    return jsonify({
        "limit": lim,
        "data": [b.to_dict() for b in items],
        "page": {"next": nxt, "more": more}
    })

@bp.get("")
def list_books():
    raw = request.args.get("cursor")
    lim = min(request.args.get("limit", 20, type=int), 100)
    sort = request.args.get("sort", "-id")
    cat = request.args.get("category", type=int)

    p, cols, desc = parse_sort(sort)
    if p is None:
        return jsonify({"error": cols}), 400

    q = select(Book).order_by(*cols)
    if cat:
        q = q.filter(Book.category_id == cat)

    q, err, code = apply_cursor(q, raw, sort, p, desc)
    if err:
        return jsonify({"e": err}), code
    
    rows = db.session.scalars(q.limit(lim + 1)).all()

    return build_response(
        rows[:lim], lim, sort, p, len(rows) > lim
    )

@bp.get("/<int:book_id>")
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict()), 200

@bp.post("")
def create_book():
    payload = request.get_json(silent=True) or {}
    try:
        validate(payload, SCHEMA)
    except ValidationError as e:
        return jsonify({
            "error": "validation_failed",
            "field": list(e.path),
            "message": e.message
        }), 400

    book_id = payload.get("id")
    title = payload.get("title")
    isbn = payload.get("isbn")
    price_data = payload.get("price", {})
    amount = price_data.get("amount", 0)

    book = Book(
        custom_id=book_id,
        title=title,
        isbn=isbn,
        price_vnd=amount
    )

    authors_payload = payload.get("authors", [])
    for auth_info in authors_payload:
        author_id = auth_info.get("id")
        author = Author.query.get(author_id)
        if not author and "name" in auth_info:
            author = Author(id=author_id, name=auth_info["name"])
            db.session.add(author)
        if author:
            book.authors.append(author)

    db.session.add(book)
    db.session.commit()

    return jsonify(book.to_dict()), 201

@bp.delete("/<int:book_id>")
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "deleted"}), 200