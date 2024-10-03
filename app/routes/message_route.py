from flask import Blueprint, request, make_response, jsonify, render_template, Response
from flask_jwt_extended import create_access_token, jwt_required, decode_token, get_jwt_identity
from app.models.category_model import Category

message_bp : Blueprint = Blueprint("message_bp", __name__)

@message_bp.route("/")
def index() -> str:
    return render_template("prueba.html")



from flask_socketio import SocketIO

def register_websocket_events(socketio: SocketIO):
   
    # Evento de conexión Socket.IO
    @socketio.on('message')
    def handle_message(msg):
        print(f'Mensaje recibido: {msg}')
        socketio.send(f'Eco: {msg}')  # Responde y lo difunde a todos los clientes conectados

    @socketio.on('connect')
    def handle_connect():
        print('Cliente conectado')

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Cliente desconectado')

