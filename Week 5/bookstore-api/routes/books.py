from flask import Blueprint, request, jsonify
from jsonschema import validate, ValidationError
import json
from models import db, Book, Author

bp = Blueprint('books', __name__)
SCHEMA = json.load(open("schemas/book.json"))

@bp.get("")
def get_books():
    books = Book.query.all()
    return jsonify([b.to_dict() for b in books]), 200

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
        id=book_id,
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