from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

USERS = {
    1: {"id": 1, "name": "User 1", "followers": [], "following": []},
    2: {"id": 2, "name": "User 2", "followers": [], "following": []},
    3: {"id": 3, "name": "User 3", "followers": [], "following": []},
    4: {"id": 4, "name": "User 4", "followers": [], "following": []},
    5: {"id": 5, "name": "User 5", "followers": [], "following": []}
}

POSTS = {
    1: {"id": 1, "user_id": 1, "comments": [], "tags": ["comedy"]},
    2: {"id": 2, "user_id": 1, "comments": [], "tags": []},
    3: {"id": 3, "user_id": 2, "comments": [], "tags": []},
    4: {"id": 4, "user_id": 3, "comments": [], "tags": []},
    5: {"id": 5, "user_id": 4, "comments": [], "tags": []},
    6: {"id": 6, "user_id": 5, "comments": [], "tags": []}
}

_next_post = 7

@app.get("/posts")
def list_all_posts():
    tag = request.args.get("tag")

    if tag is None:
        return jsonify(POSTS), 200

    result = [post for post in POSTS.values() if tag in post["tags"]]

    return jsonify(result), 200

@app.get("/users/<int:uid>/posts")
def list_user_posts(uid):
    if uid not in USERS:
        return jsonify(error="user not found"), 404

    result = [post for post in POSTS.values() if post["user_id"] == uid]

    return jsonify(result), 200

@app.post("/users/<int:uid>")
def write_post(uid):
    if uid not in USERS:
        return jsonify(error="user not found"), 404

    global _next_post

    post = request.get_json(silent=True) or {}
    tags = post.get("tags")
    if not tags:
        return jsonify(error="require tags"), 422

    post = {"id": _next_post, "user_id": uid, "comments": [], "tags":tags}
    POSTS[_next_post] = post

    _next_post += 1

    return jsonify(post), 201

if (__name__ == "__main__"):
    app.run(host="127.0.0.1", port=5000, debug=True)