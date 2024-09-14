from flask import Blueprint, request, make_response, jsonify, render_template, Response
from flask_jwt_extended import create_access_token, jwt_required, decode_token, get_jwt_identity
from datetime import timedelta
from app.models.product_model import Product
from app.models.store_model import Store

product_bp : Blueprint = Blueprint("product_bp", __name__)

@product_bp.route("/api/product/getall", methods=['GET'])
def get_products() -> tuple[Response,int]:
    products : list = Product.get_all()
    return jsonify(products), 200

@product_bp.route("/api/product/<id>", methods=['GET'])
def get_product(id : str) -> tuple[Response,int]:
    product : dict | None = Product.get_one(id)
    print(product)
    return (jsonify(product), 200) if product else (jsonify({"message": "Product not found"}), 404)

@product_bp.route("/api/product/create", methods=['POST'])
def create_product() -> tuple[Response,int]:
    data : dict = request.get_json()
    product_created : bool = Product.add_one(data)
    return(jsonify({
        "message": "Product created successfully"
        }), 201 )if product_created else (jsonify({
        "message": "Product was not created"
        }),400)

@product_bp.route("/api/product/delete/<id>", methods=['DELETE'])
def delete_product(id : str) -> tuple[Response,int]:
    product_deleted : bool = Product.delete(id)
    return (jsonify({
        "message": "Product deleted successfully"
        }), 200) if product_deleted else (jsonify({
        "message": "Product not found"
        }), 404)

@product_bp.route("/api/product/getfrom/<id_store>", methods=['GET'])
def get_products_from(id_store : str) -> tuple[Response,int]:
    data : dict = request.get_json()
    field : str | None = data.get("field")
    order : int | None = data.get("order")
    store_inventory : list = Store.get_store_inventory(id_store)
    products : list | None= Product.get_all_from(store_inventory, field, order) if field and order else None
    return (jsonify(products), 200) if len(store_inventory) > 0 and products else (jsonify({
        "message": "Error al cargar inventario"}
        ), 400)