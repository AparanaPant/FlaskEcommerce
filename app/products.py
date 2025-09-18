# app/products.py
from flask import request
from flask_restx import Namespace, Resource, fields
from .database import db
from .models import Product

ns = Namespace("products", description="Product catalog")

product_model = ns.model("Product", {
    "id": fields.Integer(readonly=True),
    "name": fields.String(required=True),
    "description": fields.String,
    "price_cents": fields.Integer(required=True, example=7500),
})

list_model = ns.model("ProductList", {
    "products": fields.List(fields.Nested(product_model))
})

@ns.route("")
class Products(Resource):
    @ns.marshal_with(list_model)
    def get(self):
        products = Product.query.all()
        return {"products": [
            {"id": p.id, "name": p.name, "description": p.description, "price_cents": p.price_cents}
            for p in products
        ]}

@ns.route("/seed")
class Seed(Resource):
    @ns.expect(ns.model("SeedInput", {
        "products": fields.List(fields.Nested(product_model), required=False)
    }), validate=False)
    def post(self):
        data = request.get_json(silent=True) or {}
        items = data.get("products") or [
            {"name": "Keyboard", "description": "Mechanical keyboard", "price_cents": 7500},
            {"name": "Mouse", "description": "Wireless mouse", "price_cents": 3500},
            {"name": "Monitor", "description": "27 inch 1440p", "price_cents": 22000},
        ]
        for item in items:
            db.session.add(Product(name=item["name"],
                                   description=item.get("description"),
                                   price_cents=item["price_cents"]))
        db.session.commit()
        return {"inserted": len(items)}
