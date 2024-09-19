from flask import Blueprint, request, make_response, jsonify, render_template, Response
from flask_jwt_extended import create_access_token, jwt_required, decode_token, get_jwt_identity
from app.models.featured_model import Featured
from app.models.store_model import Store


featured_bp : Blueprint = Blueprint("featured_bp", __name__)

@featured_bp.route("/api/featured/getall", methods=["GET"])
def get_featured() -> tuple[Response,int]:
    featured : list = Featured.get_all_featured()
    return jsonify(featured),200

@featured_bp.route("/api/featured/create", methods=["POST"])
def create_feature()-> tuple[Response,int]:
    data : dict = request.get_json()
    return (jsonify({
        "message":"Category created"
        }), 200) if Featured.create_feature(data) else (jsonify({
        "message":"Category not created"
        }), 400)
    
@featured_bp.route("/api/featured/getfrom/", methods=['GET'])
def get_products_from() -> tuple[Response,int]:
    stores : list | None = Store.get_all_stores()
    featured_list : list = Featured.setInfo(stores)
    return (jsonify(featured_list), 200) if len(featured_list) > 0 else (jsonify({
        "message": "Error al cargar inventario"}
        ), 400)

