from flask import Blueprint, request, make_response, jsonify, render_template, Response
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    decode_token,
    get_jwt_identity,
)
from app.models.order_model import Order


order_bp: Blueprint = Blueprint("order_bp", __name__)


@order_bp.route("/api/order/getall/<type>", methods=["GET"])
@jwt_required()
def get_orders(type: str) -> tuple[Response, int]:
    try:
        user_id = get_jwt_identity()
        orders: list = Order.get_all_from(user_id, type)
        return jsonify({"orders": orders}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@order_bp.route("/api/order/all_pending", methods=["GET"])
@jwt_required()
def get_all_pending_orders() -> tuple[Response, int]:
    orders: list = Order.get_pending()
    return jsonify(orders), 200


@order_bp.route("/api/order/create", methods=["POST"])
@jwt_required()
def create_order() -> tuple[Response, int]:
    data_json: dict = request.get_json()
    try:
        user_id = get_jwt_identity()
        data: dict = {
            "customer": user_id,
            "products": data_json.get("products"),
            "total": data_json.get("total"),
            "store": data_json.get("store"),
            "destiny": data_json.get("destiny"),
        }

        order_created_id: str | None = Order.create_order(data)

        return (
            (
                jsonify(
                    {
                        "message": "Order created",
                        "success": True,
                        "id": order_created_id,
                    }
                ),
                201,
            )
            if order_created_id is not None
            else (jsonify({"message": "Order not created", "success": False}), 400)
        )
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@order_bp.route("/api/order/active/<type>", methods=["GET"])
@jwt_required()
def active_order(type: str) -> tuple[Response, int]:
    try:
        user_id: str = get_jwt_identity()
        orders: list = Order.get_orders_active(user_id, type)
        return jsonify({"orders": orders}), 200
    except:
        return jsonify({"error": "Unauthorized"}), 401


@order_bp.route("/api/order/<id>")
@jwt_required()
def get_order(id: str) -> tuple[Response, int]:
    try:
        order: dict | None = Order.get_one_order(id)
        return (
            (jsonify(order), 200)
            if order
            else (jsonify({"error": "Order not found"}), 404)
        )
    except:
        return jsonify({"error": "Order not found"}), 404


@order_bp.route("/api/order/changestatus/<status>/<id>", methods=["PUT"])
def change_status(status: str, id: str) -> tuple[Response, int]:
    order_changed: bool = Order.change_order_status(id, status)
    return (
        (jsonify({"message": "Successful", "success": True}), 200)
        if order_changed
        else (
            jsonify(
                {"message": "Error al cambiar el status de la orden", "success": False}
            ),
            400,
        )
    )


@order_bp.route("/api/order/accept", methods=["PUT"])
@jwt_required()
def accept_order() -> tuple[Response, int]:
    data_json: dict = request.get_json()
    try:
        user_id = get_jwt_identity()
        order_id = data_json["order_id"]
        result = Order.accept_order(order_id, user_id)
        return (jsonify({"success": result}), 200)
    except:
        return jsonify({"error": "Error al aceptar la orden"}), 400


@order_bp.route("/api/order/send_message", methods=["PUT"])
@jwt_required()
def send_message() -> tuple[Response, int]:
    data_json: dict = request.get_json()
    try:
        user_id = get_jwt_identity()
        order_id = data_json["order_id"]
        message = data_json["message"]
        time = data_json["time"]
        result = Order.send_message(order_id, user_id, message, time)
        return (jsonify({"success": result}), 200)
    except:
        return jsonify({"error": "Error al mandar mensaje"}), 400
