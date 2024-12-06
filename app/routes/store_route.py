from flask import Blueprint, request, make_response, jsonify, render_template, Response
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    decode_token,
    get_jwt_identity,
)
from app.models.store_model import Store
from app.models.category_model import Category
from app.models.product_model import Product

store_bp: Blueprint = Blueprint("store_bp", __name__)


@store_bp.route("/api/store/register", methods=["POST"])
def register_store2() -> tuple[Response, int]:
    data: dict = request.get_json()
    return (
        (jsonify({"message": "Registro exitoso"}), 201)
        if Store.register_store(data)
        else (jsonify({"message": "Error en el registro"}), 400)
    )


@store_bp.route("/api/store/addinventory/<id>", methods=["PUT"])
def add_inventory(id: str) -> tuple[Response, int]:
    data: list = request.get_json()
    return (
        (jsonify({"message": "Inventario agregado exitosamente"}), 200)
        if Store.add__product_inventory(id, data)
        else (jsonify({"message": "Error al agregar inventario"}), 400)
    )


@store_bp.route("/api/store/addproducts/<id>", methods=["GET"])
def template2(id: str):
    productos: list = Product.get_all()
    return render_template("add_products.html", productos=productos, id=id)


@store_bp.route("/api/store/addproducts/<id>", methods=["POST"])
def add_products(id: str) -> tuple[Response, int]:
    data: list = request.get_json()
    return (
        (jsonify({"message": "Inventario agregado exitosamente"}), 200)
        if Store.add__product_inventory(id, data)
        else (jsonify({"message": "Error al agregar inventario"}), 400)
    )


@store_bp.route("/api/store/stock/<id>", methods=["GET"])
def template3(id: str):
    store_inventory: list = Store.get_store_inventory(id)
    productos: list = Product.get_all_from(store_inventory, None, None)
    return render_template("enable_product.html", productos=productos, id=id)


@store_bp.route("/api/store/stock/<id>/<enable>", methods=["POST"])
def stock(id: str, enable: str) -> tuple[Response, int]:
    data: list = request.get_json()
    return (
        (jsonify({"message": "Inventario agregado exitosamente"}), 200)
        if Store.product_inventory(id, data, enable == "enable")
        else (jsonify({"message": "Error al agregar inventario"}), 400)
    )


@store_bp.route("/api/store/<id>", methods=["GET"])
def get_store(id: str) -> tuple[Response, int]:
    store: dict | None = Store.get_store_by_id(id)
    return (
        (jsonify(store), 200)
        if store
        else (jsonify({"message": "No se encontró el almacen"}), 400)
    )


@store_bp.route("/api/store/deleteinventory/<id>", methods=["PUT"])
def delete_inventory(id: str) -> tuple[Response, int]:
    data: list = request.get_json()
    return (
        (jsonify({"message": "Inventario eliminado exitosamente"}), 200)
        if Store.delete_product_inventory(id, data)
        else (jsonify({"message": "Error al borrar inventario"}), 400)
    )


@store_bp.route("/api/store/getall", methods=["GET"])
def get_all_stores() -> tuple[Response, int]:
    stores: list = Store.get_all_stores()
    return (
        (jsonify(stores), 200)
        if stores
        else (jsonify({"message": "No se encontraron almacenes"}), 400)
    )


@store_bp.route("/api/store/", methods=["GET"])
def template() -> str:
    ubicaciones: list = ["Central", "Salud", "Ingeniería"]
    categorias: list = [
        category["name"] for category in Category.get_category_stores(True)
    ]
    return render_template(
        "store_registry.html", ubicaciones=ubicaciones, categorias=categorias
    )


@store_bp.route("/api/store/register_v", methods=["POST"])
def register_store() -> tuple[Response, int] | str:

    nombre = request.form.get("nombre")
    ubicacion = request.form.get("ubicacion")
    longitud = request.form.get("longitud")
    latitud = request.form.get("latitud")
    categoria = request.form.get("categoria")
    descripcion = request.form.get("descripcion")

    if "imagen" not in request.files:
        return "No se seleccionó ninguna imagen"

    file = request.files["imagen"]

    if file == "":
        return "No se seleccionó ningún archivo"

    if file:
        imagen_binaria = file.read()
    else:
        imagen_binaria = None

    try:
        store: dict = {
            "name": nombre,
            "location": {"name": ubicacion, "latitude": latitud, "longitude": longitud},
            "category": categoria,
            "image": imagen_binaria,
            "description": descripcion,
        }

        return (
            (jsonify({"message": "Registro exitoso"}), 201)
            if Store.register_store(store)
            else (jsonify({"message": "Error en el registro"}), 400)
        )
    except:
        return jsonify({"message": "Error en el registro"}), 400


@store_bp.route("/api/store/review/<id>", methods=["POST"])
def getting_review(id: str) -> tuple[Response, int]:
    data: dict = request.get_json()
    response = (
        jsonify(
            {"success": True}
            if Store.get_a_review(id, data["score"])
            else {"success": False}
        ),
        200,
    )
    return response
