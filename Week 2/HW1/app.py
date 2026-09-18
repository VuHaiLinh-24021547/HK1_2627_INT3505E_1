import sqlite3
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)
ORDER_DB = "order.db"

def get_db():
    conn = sqlite3.connect(ORDER_DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product TEXT NOT NULL,
                customer TEXT NOT NULL
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM orders")

        if cursor.fetchone()[0] == 0:
            initial_orders = [
                ("Product A", "customer 1"),
                ("Prodcut B", "customer 2"),
                ("Product C", "customer 3"),
                ("Product D", "customer 4"),
                ("Product E", "customer 5"),
                ("Product F", "customer 6")
            ]

            cursor.executemany("INSERT INTO orders (product, customer) VALUES (?, ?)", initial_orders)
            conn.commit()

@app.get("/orders")
def list_order():
    with get_db() as conn:
        orders = conn.execute("SELECt * FROM orders").fetchall()
        order_list = [dict(b) for b in orders]

        return jsonify({
            "data": order_list,
            "total": len(order_list)
        }), 200

@app.post("/orders")
def create_order():
    if not request.is_json:
        return jsonify(error="expected JSON"), 415

    p = request.get_json(silent=True) or {}
    pr, c = p.get("product", "").strip(), p.get("customer", "").strip()

    if not pr or not c:
        return jsonify(error="require product and customer names"), 422

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (product, customer) VALUES (?, ?)", (pr, c))
        conn.commit()
        new_id = cursor.lastrowid

        order = {
            "id": new_id,
            "product": pr,
            "customer": c
        }

        resp = make_response(jsonify(order), 201)
        resp.headers["Location"] = f"/orders/{new_id}"

        return resp

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)