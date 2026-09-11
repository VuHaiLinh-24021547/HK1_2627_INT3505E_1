from flask import Flask, jsonify

app = Flask(__name__)

AUTHORS = [
    {"id": 1, "name": "Author 1"},
    {"id": 2, "name": "Author 2"},
    {"id": 3, "name": "Author 3"}
]

BOOKS = [
    {"id": 101, "title": "Book A", "author_id": 1},
    {"id": 102, "title": "Book B", "author_id": 1},
    {"id": 103, "title": "Book C", "author_id": 2},
    {"id": 104, "title": "Book D", "author_id": 2},
    {"id": 105, "title": "Book E", "author_id": 3},
    {"id": 106, "title": "Book F", "author_id": 3}
]

def get_all_authors():
    print("-> [DB QUERY] SELECT * FROM authors")
    return AUTHORS

def get_books_by_author(author_id):
    print(f"-> [DB QUERY] SELECT * FROM books WHERE author_id = {author_id}")
    return [b for b in BOOKS if b["author_id"] == author_id]

def get_books_by_multiple_authors(authors_id):
    print(f"-> [DB QUERY] SELECT * FROM books WHERE author_id IN {tuple(authors_id)}")
    return [b for b in BOOKS if b["author_id"] in authors_id]

@app.route("/bad", methods=["GET"])
def bad_route():
    authors = get_all_authors()

    result = []
    for author in authors:
        books = get_books_by_author(author["id"])

        result.append({
            "author": author["name"],
            "books": [b["title"] for b in books]
        })

    return jsonify(result), 200

@app.route("/good", methods=["GET"])
def good_route():
    authors = get_all_authors()

    authors_id = [a["id"] for a in authors]
    all_books = get_books_by_multiple_authors(authors_id)

    books_by_author = {}
    for book in all_books:
        books_by_author.setdefault(book["author_id"], []).append(book["title"])

    result = []
    for author in authors:
        result.append({
            "author": author["name"],
            "books": books_by_author.get(author["id"], [])
        })

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)