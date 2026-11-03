from flask import Blueprint, jsonify, request
from sqlalchemy.orm import selectinload
from extensions import db
from models.product import Product
from models.order import Order, OrderItem
from errors import NotFound, Conflict
from schemas import OrderIn, OrderOut, OrderItemIn, OrderItemOut

orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")

# 1. POST /api/v1/orders - Tạo đơn hàng chứa nhiều OrderItem
@orders_bp.post("")
def create_order():
    body = OrderIn().load(request.json or {})
    
    order = Order()
    db.session.add(order)
    
    for item_data in body["items"]:
        product_id = item_data["id"]
        qty = item_data["qty"]
        
        product = db.session.scalar(
            db.select(Product).where(Product.id == product_id, Product.archived.is_(False))
        )
        if not product:
            db.session.rollback()
            raise NotFound(message=f"Product ID {product_id} not found")
        
        if product.qty_in_stock < qty:
            db.session.rollback()
            raise Conflict(message=f"Product {product.name} (ID: {product_id}) out of stock")
        
        # Trừ số lượng kho
        product.qty_in_stock -= qty
        
        # Thêm OrderItem
        order_item = OrderItem(
            order=order,
            product_id=product.id,
            qty=qty,
            unit_price_cents=product.price_cents
        )
        db.session.add(order_item)

    db.session.commit()
    return jsonify(OrderOut().dump(order)), 201

# 2. GET /api/v1/orders - Danh sách đơn hàng (phân trang)
@orders_bp.get("")
def list_orders():
    page = max(1, int(request.args.get("page", 1)))
    size = min(100, max(1, int(request.args.get("size", 20))))

    # Sử dụng selectinload(Order.items) để eager load danh sách items
    stmt = (
        db.select(Order)
        .options(selectinload(Order.items))
        .order_by(Order.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    rows = db.session.execute(stmt).scalars().all()
    total = db.session.scalar(db.select(db.func.count()).select_from(Order))

    return jsonify({
        "items": [OrderOut().dump(o) for o in rows],
        "page": page,
        "size": size,
        "total": total
    }), 200

# 3. GET /api/v1/orders/<int:id> - Chi tiết đơn hàng
@orders_bp.get("/<int:id>")
def get_order(id):
    order = db.session.get(Order, id)
    if not order:
        raise NotFound(message="Order not found")
    return jsonify(OrderOut().dump(order)), 200

# 4. POST /api/v1/orders/<int:id>/items - Thêm 1 OrderItem vào đơn hàng đã tồn tại
@orders_bp.post("/<int:id>/items")
def add_order_item(id):
    order = db.session.get(Order, id)
    if not order:
        raise NotFound(message="Order not found")

    item_data = OrderItemIn().load(request.json or {})
    product = db.session.scalar(
        db.select(Product).where(Product.id == item_data["id"], Product.archived.is_(False))
    )
    if not product:
        raise NotFound(message=f"Product ID {item_data['id']} not found")

    if product.qty_in_stock < item_data["qty"]:
        raise Conflict(message=f"Product {product.name} out of stock")

    product.qty_in_stock -= item_data["qty"]

    order_item = OrderItem(
        order=order,
        product_id=product.id,
        qty=item_data["qty"],
        unit_price_cents=product.price_cents
    )
    db.session.add(order_item)
    db.session.commit()

    return jsonify(OrderItemOut().dump(order_item)), 201

# 5. DELETE /api/v1/orders/<int:id> - Xóa đơn hàng
@orders_bp.delete("/<int:id>")
def delete_order(id):
    order = db.session.get(Order, id)
    if not order:
        raise NotFound(message="Order not found")
    
    db.session.delete(order)
    db.session.commit()
    return "", 204