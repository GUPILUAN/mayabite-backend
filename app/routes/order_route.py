from flask import Blueprint, request, make_response, jsonify, render_template, Response
from flask_jwt_extended import create_access_token, jwt_required, decode_token, get_jwt_identity
from app.models.order_model import Order


order_bp : Blueprint = Blueprint("order_bp", __name__)

@order_bp.route("/api/order/getall/<type>/<id>", methods=["GET"])
def get_orders(type: str, id : str) -> tuple[Response,int]:
    orders:list = Order.get_all_from(id,type)
    return jsonify(orders),200

@order_bp.route("/api/order/create", methods=["POST"])
def create_order()-> tuple[Response,int]:
    data : dict = request.get_json()
    return (jsonify({
        "message":"Order created"
        }), 200) if Order.create_order(data) else (jsonify({
        "message":"Order not created"
        }), 400)
    
@order_bp.route("/api/order/changestatus/<status>/<id>", methods=['PUT'])
def change_status(status:str, id:str) -> tuple[Response,int]:
    order_changed : bool = Order.change_order_status(id,status)
    return (jsonify({"message" : "Successful"}), 200) if order_changed else (jsonify({
        "message": "Error al cargar inventario"}
        ), 400)