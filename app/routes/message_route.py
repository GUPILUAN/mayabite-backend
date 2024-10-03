from flask import Blueprint, request, make_response, jsonify, render_template, Response
from flask_jwt_extended import create_access_token, jwt_required, decode_token, get_jwt_identity
from app.models.category_model import Category

message_bp : Blueprint = Blueprint("message_bp", __name__)

@message_bp.route("/")
def index() -> str:
    return render_template("prueba.html")