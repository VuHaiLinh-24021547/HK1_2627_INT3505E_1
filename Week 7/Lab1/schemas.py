from marshmallow import Schema, fields, validate

# Output Schema
class ProductOut(Schema):
    id = fields.Int()
    sku = fields.Str()
    name = fields.Str()
    description = fields.Str(allow_none=True)
    price_cents = fields.Int()
    qty_in_stock = fields.Int()
    archived = fields.Bool()

# Input Schema cho POST /api/v1/products
class ProductIn(Schema):
    sku = fields.Str(required=True, validate=validate.Length(min=3, max=32))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True, required=False)
    price_cents = fields.Int(required=True, validate=validate.Range(min=0))
    qty_in_stock = fields.Int(load_default=0, validate=validate.Range(min=0))

# Schema cho PATCH /api/v1/products/<int:id>
class ProductPatch(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True)
    price_cents = fields.Int(validate=validate.Range(min=0))
    qty_in_stock = fields.Int(validate=validate.Range(min=0))

# Schema cho POST /api/v1/products/<int:id>/reserve
class ReserveIn(Schema):
    qty = fields.Int(required=True, validate=validate.Range(min=1))

class OrderItemIn(Schema):
    id = fields.Int(required=True)
    qty = fields.Int(required=True, validate=validate.Range(min=1))

class OrderItemOut(Schema):
    id = fields.Int()
    product_id = fields.Int()
    qty = fields.Int()
    unit_price_cents = fields.Int()
    
class OrderIn(Schema):
    items = fields.List(
        fields.Nested(OrderItemIn),
        required=True,
        validate=validate.Length(min=1)
    )

class OrderOut(Schema):
    id = fields.Int()
    created_at = fields.DateTime()
    items = fields.List(fields.Nested(OrderItemOut))
    total_cents = fields.Method("get_total_cents")

    def get_total_cents(self, obj):
        return sum(item.qty * item.unit_price_cents for item in obj.items)