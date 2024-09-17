from flask import Blueprint, request, make_response, jsonify, render_template, Response
from flask_jwt_extended import create_access_token, jwt_required, decode_token, get_jwt_identity
from app.models.category_model import Category

category_bp : Blueprint = Blueprint("category_bp", __name__)

@category_bp.route("/api/category/getall", methods=["GET"])
def get_categories() -> tuple[Response,int]:
    categories : list = Category.get_all_categories()
    return jsonify(categories),200

@category_bp.route("/api/category/create", methods=["POST"])
def create_category()-> tuple[Response,int]:
    data : dict = request.get_json()
    return (jsonify({
        "message":"Category created"
        }), 200) if Category.create_category(data) else (jsonify({
        "message":"Category not created"
        }), 400)
    

