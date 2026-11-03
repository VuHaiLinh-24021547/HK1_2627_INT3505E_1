import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from sqlalchemy import event
from extensions import db as _db
from __init__ import create_app
from models.product import Product

@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "PRESERVE_CONTEXT_ON_EXCEPTION": False
    })
    
    with app.app_context():
        _db.create_all()
        # Seed 5 sản phẩm mẫu dùng cho testing
        products = [
            Product(sku=f"TEST-{i}", name=f"Test Prod {i}", price_cents=1000, qty_in_stock=50)
            for i in range(1, 6)
        ]
        _db.session.add_all(products)
        _db.session.commit()
        
        yield app
        
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

# Context Manager theo dõi và đếm số câu lệnh SQL gửi đến SQLite
class QueryCounter:
    def __init__(self, engine):
        self.engine = engine
        self.count = 0

    def __enter__(self):
        event.listen(self.engine, "before_cursor_execute", self._callback)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        event.remove(self.engine, "before_cursor_execute", self._callback)

    def _callback(self, conn, cursor, statement, parameters, context, executemany):
        self.count += 1

@pytest.fixture
def capture_queries(app):
    return lambda: QueryCounter(_db.engine)