from flask import Flask, jsonify, request

app = Flask(__name__)

BOOKS = [{"t":"Python Tutorial"}, 
         {"t":"Java Tutorial"},
         {"t":"C Tutorial"},
         {"t":"Huge Python"}]

@app.route("/books", methods=["GET"])
def list_books():
    limit = int(request.args.get("limit", 20))
    q = request.args.get("q","").strip().lower()
    items = [b for b in BOOKS if q in b["t"].lower()]
    return jsonify({"items": items[:limit]}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)