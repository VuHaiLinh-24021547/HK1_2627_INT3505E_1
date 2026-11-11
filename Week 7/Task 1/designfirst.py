import connexion

products_db = {
    1: {"id": 1, "name": "Product 1", "price": 1200.0},
    2: {"id": 2, "name": "Product 2", "price": 800.0},
}

def get_products():
    return list(products_db.values()), 200

def create_product(body):
    new_id = max(products_db.keys(), default=0) + 1
    product = {"id": new_id, **body}
    products_db[new_id] = product
    return product, 201

def get_product_by_id(product_id):
    product = products_db.get(product_id)
    if not product:
        return {"detail": "Không tìm thấy sản phẩm", "status": 404}, 404
    return product, 200


app = connexion.FlaskApp(__name__, specification_dir="./")
app.add_api("product.yaml")

if __name__ == "__main__":
    app.run()