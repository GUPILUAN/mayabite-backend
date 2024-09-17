from flask import Blueprint, request, make_response, jsonify, render_template, Response
from flask_jwt_extended import create_access_token, jwt_required, decode_token, get_jwt_identity
from app.models.location_model import Location

location_bp : Blueprint = Blueprint("location_bp", __name__)

@location_bp.route("/api/location/getall", methods=["GET"])
def get_locations() -> tuple[Response,int]:
    locations : list = Location.get_all_locations()
    return jsonify(locations),200

@location_bp.route("/api/location/create", methods=["POST"])
def create_location()-> tuple[Response,int]:
    data : dict = request.get_json()
    return (jsonify({
        "message":"Location created"
        }), 200) if Location.create_location(data) else (jsonify({
        "message":"Location not created"
        }), 400)
    