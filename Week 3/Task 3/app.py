import base64
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

ORDERS = [
    {"id": 1, "product": "Product 1", "status": "paid", "customer_id": 101, "total": 150.0},
    {"id": 2, "product": "Product 2", "status": "delivered", "customer_id": 102, "total": 200.0},
    {"id": 3, "product": "Product 3", "status": "shipped", "customer_id": 101, "total": 50.0},
    {"id": 4, "product": "Product 4", "status": "paid", "customer_id": 103, "total": 300.0},
    {"id": 5, "product": "Product 5", "status": "processing", "customer_id": 102, "total": 120.0},
    {"id": 6, "product": "Product 6", "status": "delivered", "customer_id": 104, "total": 80.0},
    {"id": 7, "product": "Product 7", "status": "paid", "customer_id": 101, "total": 210.0},
    {"id": 8, "product": "Product 8", "status": "cancelled", "customer_id": 105, "total": 45.0},
    {"id": 9, "product": "Product 9", "status": "shipped", "customer_id": 103, "total": 110.0},
    {"id": 10, "product": "Product 10", "status": "paid", "customer_id": 102, "total": 95.0},
    {"id": 11, "product": "Product 11", "status": "delivered", "customer_id": 101, "total": 175.0},
    {"id": 12, "product": "Product 12", "status": "processing", "customer_id": 104, "total": 60.0},
    {"id": 13, "product": "Product 13", "status": "paid", "customer_id": 103, "total": 250.0},
    {"id": 14, "product": "Product 14", "status": "shipped", "customer_id": 105, "total": 130.0},
    {"id": 15, "product": "Product 15", "status": "delivered", "customer_id": 102, "total": 400.0},
    {"id": 16, "product": "Product 16", "status": "paid", "customer_id": 101, "total": 85.0},
    {"id": 17, "product": "Product 17", "status": "processing", "customer_id": 103, "total": 190.0},
    {"id": 18, "product": "Product 18", "status": "delivered", "customer_id": 104, "total": 220.0},
    {"id": 19, "product": "Product 19", "status": "paid", "customer_id": 105, "total": 310.0},
    {"id": 20, "product": "Product 20", "status": "shipped", "customer_id": 102, "total": 105.0}
]

def encode_cursor(last_id):
    raw_json = json.dumps({"last_id": last_id})
    return base64.b64encode(raw_json.encode('utf-8')).decode('utf-8')

def decode_cursor(cursor_str):
    try:
        decoded_bytes = base64.b64decode(cursor_str.encode('utf-8'), validate=True)
        data = json.loads(decoded_bytes.decode('utf-8'))
        if isinstance(data, dict) and "last_id" in data:
            return data["last_id"]
        raise ValueError("Cấu trúc payload cursor không hợp lệ")
    except Exception:
        raise ValueError("Cursor không thể giải mã")

@app.get("/orders")
def list_orders():
    filtered_orders = list(ORDERS)

    status = request.args.get("status")
    if status:
        filtered_orders = [o for o in filtered_orders if o.get("status") == status]

    customer_id = request.args.get("customer_id")
    if customer_id:
        filtered_orders = [o for o in filtered_orders if o.get("customer_id") == customer_id]

    sort_parameter = request.args.get("sort")
    if sort_parameter:
        filtered_orders.sort(key=lambda x: x.get(sort_parameter))

    limit_parameter = request.args.get("limit", default=10)
    limit = int(limit_parameter)

    cursor_parameter = request.args.get("cursor")
    start_index = 0

    if cursor_parameter:
        try:
            last_id = decode_cursor(cursor_parameter)
            cursor_index = next((i for i, o in enumerate(filtered_orders) if o.get("id") == last_id), None)
            if cursor_index is None:
                return jsonify({"error": "broken cursor or order not found"}), 400
            start_index = cursor_index + 1
        except ValueError:
            return jsonify({"error": "Invalid cursor format"}), 400

    page_items = filtered_orders[start_index : start_index + limit]

    next_cursor = None
    if (start_index + limit) < len(filtered_orders) and len(page_items) > 0:
        next_cursor = encode_cursor(page_items[-1]['id'])

    fields_parameter = request.args.get("fields")
    if fields_parameter:
        request_fields = [f.strip() for f in fields_parameter.split(",") if f.strip()]
        result_data = [
            {field: item.get(field) for field in request_fields if field in item}
            for item in page_items
        ]
    else:
        result_data = page_items

    return jsonify({
        "data": result_data,
        "pagination": {
            "limit": limit,
            "next_cursor": next_cursor,
        }
    }), 200

if (__name__ == "__main__"):
    app.run(host="127.0.0.1", port=5000, debug=True)