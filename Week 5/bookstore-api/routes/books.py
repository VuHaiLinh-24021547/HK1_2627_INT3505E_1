from flask import Blueprint, request, jsonify
from jsonschema import validate, ValidationError
import json
import base64
from sqlalchemy import select, tuple_, func
from models import db, Book, Author, Category

bp = Blueprint('books', __name__)
SCHEMA = json.load(open("./schemas/book.json"))

SORT = {
    "id": Book.id,
    "price": Book.price_vnd,
    "title": Book.title
}

def parse_sort(raw):
    if not raw:
        raw = "-id"

    sort_keys = [s.strip() for s in raw.split(",") if s.strip()]
    cols = []
    primary_col = None
    primary_desc = False

    for idx, key_str in enumerate(sort_keys):
        desc = key_str.startswith("-")
        clean_key = key_str.lstrip("-")

        if clean_key not in SORT:
            return None, None, None, f"bad_sort:{clean_key}"

        col = SORT[clean_key]
        cols.append(col.desc() if desc else col.asc())

        if idx == 0:
            primary_col = col
            primary_desc = desc

    if Book.id not in [SORT[k.lstrip("-")] for k in sort_keys]:
        cols.append(Book.id.desc() if primary_desc else Book.id.asc())

    return cols, primary_col, primary_desc, None

def _enc(s):
    return base64.urlsafe_b64encode(
        json.dumps(s).encode()
    ).decode().rstrip("=")

def apply_cursor(q, raw, sort, p, desc):
    if not raw:
        return q, None, 200

    pad = "=" * (-len(raw) % 4)
    try:
        c = json.loads(base64.urlsafe_b64decode(raw + pad))
    except Exception:
        return None, "invalid_cursor", 400

    if c.get("s") != sort:
        return None, "sort_chg", 400

    v, i = c["v"], c["i"]
    op = "<" if desc else ">"

    condition = tuple_(p, Book.id).op(op)((v, i))

    return q.filter(condition), None, 200

def build_cursor_response(items, lim, sort, p, more):
    nxt = None
    if items and more:
        last = items[-1]
        nxt = _enc({
            "s": sort,
            "v": getattr(last, p.key),
            "i": last.id
        })
    return jsonify({
        "strategy": "cursor",
        "limit": lim,
        "data": [b.to_dict() for b in items],
        "page": {"next": nxt, "more": more}
    })

@bp.get("")
def list_books():
    strategy = request.args.get("strategy", "cursor")
    lim = min(request.args.get("limit", 20, type=int), 100)
    sort = request.args.get("sort", "-id")
    cat = request.args.get("category", type=int)
    genre = request.args.get("genre")

    cols, p, desc, err = parse_sort(sort)
    if err:
        return jsonify({"error": err}), 400

    q = select(Book)

    if cat:
        q = q.filter(Book.category_id == cat)
    if genre:
        q = q.join(Book.category).filter((Category.slug == genre) | (Category.name == genre))

    q = q.order_by(*cols)

    if strategy == "offset":
        page = max(request.args.get("page", 1, type=int), 1)
        offset_val = (page - 1) * lim

        total_stmt = select(func.count()).select_from(q.subquery())
        total = db.session.scalar(total_stmt) or 0

        rows = db.session.scalars(q.offset(offset_val).limit(lim)).all()

        return jsonify({
            "strategy": "offset",
            "data": [b.to_dict() for b in rows],
            "pagination": {
                "page": page,
                "limit": lim,
                "total": total,
                "total_pages": (total + lim - 1) // lim if lim else 1
            }
        }), 200

    raw_cursor = request.args.get("cursor")
    q, err_msg, code = apply_cursor(q, raw_cursor, sort, p, desc)
    if err_msg:
        return jsonify({"error": err_msg}), code

    rows = db.session.scalars(q.limit(lim + 1)).all()
    more = len(rows) > lim

    return build_cursor_response(
        rows[:lim], lim, sort, p, more
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
    price_vnd = payload.get("price_vnd", 0)

    book = Book(
        id=book_id,
        title=title,
        isbn=isbn,
        price_vnd=price_vnd
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