from flask import Blueprint, request, make_response, jsonify, render_template, Response
from flask_jwt_extended import create_access_token, jwt_required, decode_token, get_jwt_identity
from datetime import timedelta
from app.models.store_model import Store

store_bp : Blueprint = Blueprint("store_bp", __name__)

@store_bp.route("/api/store/register", methods=["POST"])
def register_store()-> tuple[Response, int]:
    data : dict = request.get_json()
    return (jsonify({
        "message" : "Registro exitoso"
        }), 201) if Store.register_store(data) else (jsonify({
        "message": "Error en el registro"
        }), 400)

@store_bp.route("/api/store/addinventory/<id>", methods=["PUT"])
def add_inventory(id : str) -> tuple[Response, int]:
    data : list = request.get_json()
    return (jsonify({
        "message" : "Inventario agregado exitosamente"
        }), 200) if Store.add__product_inventory(id, data) else (jsonify({
        "message": "Error al agregar inventario"}
        ), 400)

@store_bp.route("/api/store/<id>", methods=["GET"])
def get_store(id : str) -> tuple[Response, int]:
    store : dict | None = Store.get_store_by_id(id)
    return (jsonify(store), 200) if store else (jsonify({
        "message": "No se encontró el almacen"
    }), 400)

@store_bp.route("/api/store/deleteinventory/<id>", methods=["PUT"])
def delete_inventory(id : str) -> tuple[Response, int]:
    data : list = request.get_json()
    return (jsonify({
        "message" : "Inventario eliminado exitosamente"
        }), 200) if Store.delete_product_inventory(id, data) else (jsonify({
        "message": "Error al borrar inventario"}
        ), 400)