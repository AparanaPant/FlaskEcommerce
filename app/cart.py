# app/cart.py
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from .database import db
from .models import CartItem, Product, Order, OrderItem

ns = Namespace("cart", description="Cart & checkout")

add_input = ns.model("AddToCartInput", {
    "product_id": fields.Integer(required=True),
    "quantity": fields.Integer(required=False, default=1, min=1),
})

cart_item = ns.model("CartItem", {
    "product_id": fields.Integer,
    "name": fields.String,
    "quantity": fields.Integer,
    "price_cents": fields.Integer,
    "subtotal_cents": fields.Integer,
})

cart_view = ns.model("CartView", {
    "items": fields.List(fields.Nested(cart_item))
})

checkout_resp = ns.model("CheckoutResponse", {
    "message": fields.String(example="checked out"),
    "order_id": fields.Integer(example=1),
    "total_cents": fields.Integer(example=15000),
})

# Helper: show in docs that a Bearer token is expected
auth_header = {"Authorization": {"in": "header", "description": "Bearer <JWT>", "type": "string", "required": True}}

@ns.route("/add")
class AddToCart(Resource):
    @ns.expect(add_input, validate=True)
    @ns.doc(params=auth_header)
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json()
        product_id = data.get("product_id")
        quantity = int(data.get("quantity", 1))
        product = Product.query.get(product_id)
        if not product:
            ns.abort(404, "product not found")
        if quantity < 1:
            ns.abort(400, "quantity must be >= 1")

        item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
        if item:
            item.quantity += quantity
        else:
            item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
            db.session.add(item)
        db.session.commit()
        return {"message": "added", "item_id": item.id, "quantity": item.quantity}

@ns.route("")
class ViewCart(Resource):
    @ns.marshal_with(cart_view)
    @ns.doc(params=auth_header)
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        items = CartItem.query.filter_by(user_id=user_id).all()
        return {"items": [{
            "product_id": i.product_id,
            "name": i.product.name,
            "quantity": i.quantity,
            "price_cents": i.product.price_cents,
            "subtotal_cents": i.product.price_cents * i.quantity,
        } for i in items]}

@ns.route("/checkout")
class Checkout(Resource):
    @ns.marshal_with(checkout_resp)
    @ns.doc(params=auth_header)
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        items = CartItem.query.filter_by(user_id=user_id).all()
        if not items:
            ns.abort(400, "cart is empty")

        order = Order(user_id=user_id)
        db.session.add(order)
        total = 0
        for i in items:
            line_total = i.product.price_cents * i.quantity
            total += line_total
            db.session.add(OrderItem(order=order, product_id=i.product_id, quantity=i.quantity, price_cents=i.product.price_cents))
            db.session.delete(i)
        order.total_cents = total
        db.session.commit()
        return {"message": "checked out", "order_id": order.id, "total_cents": total}
