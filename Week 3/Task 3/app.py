from flask import Flask, jsonify, request

app = Flask(__name__)

ORDERS = [
    {"id": 1, "product": "Product 1", "status": "paid"},
    {"id": 2, "product": "Product 2", "status": "delivered"},
    {"id": 3, "product": "Product 3", "status": "shipped"},
    {"id": 4, "product": "Product 4", "status": "paid"},
    {"id": 5, "product": "Product 5", "status": "processing"},
    {"id": 6, "product": "Product 6", "status": "delivered"},
    {"id": 7, "product": "Product 7", "status": "paid"},
    {"id": 8, "product": "Product 8", "status": "cancelled"},
    {"id": 9, "product": "Product 9", "status": "shipped"},
    {"id": 10, "product": "Product 10", "status": "paid"},
    {"id": 11, "product": "Product 11", "status": "delivered"},
    {"id": 12, "product": "Product 12", "status": "processing"},
    {"id": 13, "product": "Product 13", "status": "paid"},
    {"id": 14, "product": "Product 14", "status": "shipped"},
    {"id": 15, "product": "Product 15", "status": "delivered"},
    {"id": 16, "product": "Product 16", "status": "paid"},
    {"id": 17, "product": "Product 17", "status": "processing"},
    {"id": 18, "product": "Product 18", "status": "delivered"},
    {"id": 19, "product": "Product 19", "status": "paid"},
    {"id": 20, "product": "Product 20", "status": "shipped"}
]



if (__name__ == "__main__"):
    app.run(host="127.0.0.1", port=5000, debug=True)