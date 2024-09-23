from app.models.order_model import Order
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

order_bp : Blueprint = Blueprint("order_bp", __name__)

@order_bp.route("/api/order/create", methods=["POST"])
@jwt_required()
def create_order():
    data : dict = request.get_json()
    order: tuple = Order.create_order(data)
    id = order[0].get("_id")
    if id:
        return jsonify(order[0]), order[1]
    
    return jsonify({"message": "Error al crear la orden"}), 400

@order_bp.route("/api/order/<order_id>", methods=["GET"])
@jwt_required()
def get_order_by_id(order_id: str):
    order: tuple = Order.get_order_by_id(order_id)
    return jsonify(order[0]), order[1]

@order_bp.route("/api/order/user", methods=["GET"])
@jwt_required()
def get_orders_by_user():
    data: dict = request.get_json()
    is_delivery_man: bool = data.get("is_delivery_man", None)
    if is_delivery_man is None:
        return jsonify({"message": "Faltan datos"}), 400
    current_user = get_jwt_identity()
    order: tuple = Order.get_orders_by_user(current_user, is_delivery_man)
    return jsonify(order[0]), order[1]

@order_bp.route("/api/order/update_status", methods=["PUT"])
@jwt_required()
def update_status():
    data: dict = request.get_json()
    order_updated = Order.update_status(data)
    if order_updated is not True:
        return jsonify({"message": "Error al actualizar el status"}), 400
    return jsonify({"message": "Status actualizado"}), 200