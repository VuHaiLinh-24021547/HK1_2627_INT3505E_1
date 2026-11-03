import pytest

# 1. Test POST /api/v1/orders
def test_create_order_success(client):
    payload = {
        "items": [
            {"id": 1, "qty": 2},
            {"id": 2, "qty": 3}
        ]
    }
    response = client.post("/api/v1/orders", json=payload)
    
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert len(data["items"]) == 2

# 2. Test GET /api/v1/orders có Eager Loading & Kiểm tra N+1
def test_list_orders_eager_loading_n_plus_1(client, capture_queries):
    # ạo sẵn 5 đơn hàng, mỗi đơn hàng có 2 items
    for _ in range(5):
        client.post("/api/v1/orders", json={
            "items": [
                {"id": 1, "qty": 1},
                {"id": 2, "qty": 1}
            ]
        })

    # Gọi GET /api/v1/orders và đo số lượng truy vấn SQL
    with capture_queries() as qc:
        response = client.get("/api/v1/orders?page=1&size=10")

    assert response.status_code == 200
    data = response.get_json()
    assert len(data["items"]) == 5

    assert qc.count <= 3, f"Phát hiện lỗi N+1! Tổng số SQL queries ghi nhận là {qc.count} (Kỳ vọng <= 3)"