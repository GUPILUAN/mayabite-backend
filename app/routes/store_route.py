from flask import Blueprint, request, make_response, jsonify, render_template, Response
from flask_jwt_extended import create_access_token, jwt_required, decode_token, get_jwt_identity
from datetime import timedelta
from app.models.store_model import Store
from app.models.category_model import Category
from app.models.location_model import Location

store_bp : Blueprint = Blueprint("store_bp", __name__)

@store_bp.route("/api/store/register", methods=["POST"])
def register_store2()-> tuple[Response, int]:
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

@store_bp.route("/api/store/getall", methods=["GET"])
def get_all_stores() -> tuple[Response, int]:
    stores : list = Store.get_all_stores()
    return (jsonify(stores), 200) if stores else (jsonify({
        "message": "No se encontraron almacenes"
        }), 400)

@store_bp.route("/api/store/", methods=["GET"])
def template():
    ubicaciones : list = [location["name"] for location in Location.get_all_locations()] 
    categorias : list = [category["name"] for category in Category.get_all_categories()]
    return render_template('store_registry.html', ubicaciones=ubicaciones, categorias=categorias)

@store_bp.route("/api/store/register_v", methods=["POST"])
def register_store():
    # Imprimir request.form y request.files para depuración
    print(f"request.form: {request.form}")
    print(f"request.files: {request.files}")

    nombre = request.form.get('nombre')
    ubicacion = request.form.get('ubicacion')
    categoria = request.form.get('categoria')
    descripcion = request.form.get('descripcion')

    if 'imagen' not in request.files:
        return "No se seleccionó ninguna imagen"
    
    file = request.files['imagen']

    if file == '':
        return "No se seleccionó ningún archivo"
    
    if file:
        imagen_binaria = file.read()
    else:
        imagen_binaria = None

    store : dict = {
        "name": nombre,
        "location": ubicacion,
        "category": categoria,
        "image": imagen_binaria,
        "description" : descripcion
    }

    return (jsonify({
        "message" : "Registro exitoso"
        }), 201) if Store.register_store(store) else (jsonify({
        "message": "Error en el registro"
        }), 400)