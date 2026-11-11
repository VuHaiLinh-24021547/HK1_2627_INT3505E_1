from flask import Flask, jsonify, request
from flask_smorest import Blueprint, abort, Api
from flask.views import MethodView
from marshmallow import Schema, fields

app = Flask(__name__)
app.config["API_TITLE"] = "Product Management API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
app.config["OPENAPI_SWAGGER_UI_VERSION"] = "5.0.0"

api = Api(app)

products_db = {
    1: {"id": 1, "name": "Product 1", "price": 1200.0},
    2: {"id": 2, "name": "Product 2", "price": 800.0},
}

class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)

blp = Blueprint("products", __name__, url_prefix="/products")

@blp.route("")
class ProductList(MethodView):
    @blp.response(200, ProductSchema(many=True))
    def get(self):
        return list(products_db.values())

    @blp.arguments(ProductSchema)
    @blp.response(201, ProductSchema)
    def post(self, new_data):
        new_id = max(products_db.keys(), default=0) + 1
        product = {"id": new_id, **new_data}
        products_db[new_id] = product
        return product

api.register_blueprint(blp)

if __name__ == "__main__":
    app.run(debug=True)