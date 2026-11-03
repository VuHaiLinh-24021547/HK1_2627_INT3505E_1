import os
from flask import Flask
from extensions import db
from errors import register_error_handlers
from api.products import products_bp
from api.orders import orders_bp
from models.product import Product
from models import order

def init_sample_data():
    count = db.session.scalar(db.select(db.func.count()).select_from(Product))
    if count == 0:
        products = [
            Product(
                sku=f"PD-{i:03d}",
                name=f"Product {i}",
                price_cents=100000,
                qty_in_stock=10
            )
            for i in range(1, 101)
        ]
        db.session.add_all(products)
        db.session.commit()

def create_app(config_override=None):
    app = Flask(__name__)

    # Cấu hình SQLite database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if config_override:
        app.config.update(config_override)

    # Khởi tạo các extension
    db.init_app(app)

    # Đăng ký Error Handlers & Blueprint
    register_error_handlers(app)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)

    # Khởi tạo bảng dữ liệu SQLite tự động
    with app.app_context():
        db.create_all()
        init_sample_data()

    return app