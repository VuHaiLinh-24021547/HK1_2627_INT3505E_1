from flask import Flask, jsonify, request, make_response

USERS = [
    {
        "id": 0,
        "name": "user A"  
    },
    {
        "id": 1,
        "name": "user B"
    }
]

POSTS = [
    {
        "id": 0,
        "user_id": 0,
        "title": "bitcoin",
        "comments": ["nice", "great"],
        "tags": ["finance", "economy"]
    },
    {
        "id": 1,
        "user_id": 1,
        "title": "little prince",
        "comments": ["nice", "great"],
        "tags": ["story"]
    }
]

app = Flask(__name__)

_next_id_post = 2
_next_id_user = 2

@app.get("/api/v1/posts")
def list_post():
    tag = request.args.get("tag", "").strip().lower()

    results = POSTS

    if tag:
        results = [result for result in results if tag in result.get("tags")]

    return jsonify(results), 200

@app.post("/api/v1/posts")
def create_post():
    global _next_id_post

    if not request.is_json:
        return jsonify(error="Expected Content-Type: application/json"), 415

    body = request.get_json(silent=True) or {}
    title = body.get("title")
    user_id = body.get("user_id")
    tags = body.get("tags")

    if not title or not user_id or not tags:
        return jsonify("require title, user id and tags"), 422

    new_post = {
        "id": _next_id_post,
        "user_id": user_id,
        "title": title,
        "comments": [],
        "tags": [tags]
    }

    POSTS.append(new_post)

    _next_id_post += 1

    resp = make_response(jsonify(new_post), 201)
    resp.headers["Location"] = f"/api/v1/posts/{new_post['id']}"
    return resp

@app.get("/api/v1/posts/<int:post_id>")
def get_post(post_id):
    post = next((p for p in POSTS if p["id"] == post_id), None)
    if not post:
        return jsonify(error="Post not found"), 404
    return jsonify(post), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)