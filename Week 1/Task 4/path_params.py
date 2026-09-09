from flask import Flask, jsonify, request

app = Flask(__name__)

BOOKS = {"abc":"ABC", "def":"DEF"}

@app.route("/books/<book_id>", methods=["GET"])
def get_book(book_id):
    book = find_by_id(book_id)
    if book is None:
        return jsonify({"error":"not found"}), 404
    return jsonify(book), 200

def find_by_id(book_id):
    if BOOKS.get(book_id) is None:
        return None

    return {book_id:BOOKS.get(book_id)}

@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    return jsonify({"id":item_id}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)