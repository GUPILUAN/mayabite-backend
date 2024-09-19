from flask import Blueprint, request, make_response, jsonify, render_template, Response
from flask_jwt_extended import create_access_token, jwt_required, decode_token, get_jwt_identity
from app.models.category_model import Category

category_bp : Blueprint = Blueprint("category_bp", __name__)

@category_bp.route("/api/category/getall", methods=["GET"])
def get_categories() -> tuple[Response,int]:
    categories : list = Category.get_all_categories()
    return jsonify(categories),200

@category_bp.route("/api/category/get/<boolean>", methods=["GET"])
def get_categories_store(boolean : str) -> tuple[Response,int]:
    categories : list = Category.get_category_stores(boolean=="true")
    return jsonify(categories),200

@category_bp.route("/api/category/create", methods=["POST"])
def create_category()-> tuple[Response,int]:
    data : dict = request.get_json()
    return (jsonify({
        "message":"Category created"
        }), 200) if Category.create_category(data) else (jsonify({
        "message":"Category not created"
        }), 400)


@category_bp.route("/api/category/", methods=["GET"])
def template():
    return render_template('create_category.html')

@category_bp.route("/api/category/register_v", methods=["POST"])
def new_category():
    nombre = request.form.get('nombre')
    is_store_category = request.form.get('tienda')

    cat : dict = {
        "name": nombre,
        "is_store_category": is_store_category == "on"
       
    }
    return (jsonify({
        "message" : "Registro exitoso"
        }), 201) if Category.create_category(cat) else (jsonify({
        "message": "Error en el registro"
        }), 400)