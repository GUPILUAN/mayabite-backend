from flask import Blueprint, request, make_response, jsonify, render_template, Response
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    decode_token,
    get_jwt_identity,
)
from datetime import timedelta
from app.models.category_model import Category
from app.models.product_model import Product
from app.models.store_model import Store

product_bp: Blueprint = Blueprint("product_bp", __name__)


@product_bp.route("/api/product/getall", methods=["GET"])
def get_products() -> tuple[Response, int]:
    products: list = Product.get_all()
    return jsonify(products), 200


@product_bp.route("/api/product/<id>", methods=["GET"])
def get_product(id: str) -> tuple[Response, int]:
    product: dict | None = Product.get_one(id)
    return (
        (jsonify(product), 200)
        if product
        else (jsonify({"message": "Product not found"}), 404)
    )


@product_bp.route("/api/product/create", methods=["POST"])
def create_product() -> tuple[Response, int]:
    data: dict = request.get_json()
    product_created: bool = Product.add_one(data)
    return (
        (jsonify({"message": "Product created successfully"}), 201)
        if product_created
        else (jsonify({"message": "Product was not created"}), 400)
    )


@product_bp.route("/api/product/delete/<id>", methods=["DELETE"])
def delete_product(id: str) -> tuple[Response, int]:
    product_deleted: bool = Product.delete(id)
    return (
        (jsonify({"message": "Product deleted successfully"}), 200)
        if product_deleted
        else (jsonify({"message": "Product not found"}), 404)
    )


@product_bp.route("/api/product/getfrom/<id_store>", methods=["GET"])
def get_products_from(id_store: str) -> tuple[Response, int]:
    try:
        data: dict = request.get_json()
    except:
        data = {}
    field: str | None = data.get("field")
    order: int | None = data.get("order")
    store_inventory: list = Store.get_store_inventory(id_store)
    products: list | None = Product.get_all_from(store_inventory, field, order)
    return (
        (jsonify(products), 200)
        if len(store_inventory) > 0
        else (jsonify({"message": "Error al cargar inventario"}), 404)
    )


@product_bp.route("/api/product/", methods=["GET"])
def template():
    categorias: list = [
        category["name"] for category in Category.get_category_stores(False)
    ]
    return render_template("product_registry.html", categorias=categorias)


@product_bp.route("/api/product/register_v", methods=["POST"])
def register_product():
    nombre: str | None = request.form.get("nombre")
    categoria: str | None = request.form.get("categoria")
    descripcion: str | None = request.form.get("descripcion")
    precio: str | None = request.form.get("precio")

    if "imagen" not in request.files:
        return "No se seleccionó ninguna imagen"

    file = request.files["imagen"]

    if file == "":
        return "No se seleccionó ningún archivo"

    if file:
        imagen_binaria = file.read()
    else:
        imagen_binaria = None

    prod: dict = {
        "name": nombre,
        "category": categoria,
        "price": float(precio) if precio else 0,
        "image": imagen_binaria,
        "description": descripcion,
    }

    return (
        (jsonify({"message": "Registro exitoso"}), 201)
        if Product.add_one(prod)
        else (jsonify({"message": "Error en el registro"}), 400)
    )
