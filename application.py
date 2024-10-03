from flask import Flask
from flask_socketio import SocketIO,emit
from app import create_app

app: Flask
socket_io: SocketIO

(app, socket_io) = create_app()

# Evento cuando un cliente se conecta
@socket_io.on('connect')
def handle_connect():
    print('Cliente conectado')
    emit('response', {'data': 'Conexión exitosa'})  # Enviar respuesta al cliente

# Evento cuando se desconecta un cliente
@socket_io.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado')

# Evento para manejar mensajes desde el cliente
@socket_io.on('message')
def handle_message(data):
    print(f'Mensaje recibido: {data}')
    emit('response', {'data': f'Servidor recibió: {data}'})  # Enviar respuesta al cliente

# Otro ejemplo para un evento personalizado llamado 'custom_event'
@socket_io.on('custom_event')
def handle_custom_event(data):
    print(f'Evento personalizado recibido: {data}')
    emit('response', {'data': 'Recibido en custom_event'})
# DEV
#if __name__ == "__main__":
    # Usamos socket_io.run en lugar de app.run() para que maneje WebSockets
    #socket_io.run(app, debug=True, host="0.0.0.0", port=8080)
    