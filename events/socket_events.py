from flask_socketio import SocketIO

def register_websocket_events(socket_io: SocketIO):
    @socket_io.on('connect')
    def handle_connect():
        print('Cliente conectado')
        socket_io.emit('response', {'data': 'Conexión exitosa'})  # Enviar respuesta al cliente

    # Evento cuando se desconecta un cliente
    @socket_io.on('disconnect')
    def handle_disconnect():
        print('Cliente desconectado')

    # Evento para manejar mensajes desde el cliente
    @socket_io.on('message')
    def handle_message(data):
        print(f'Mensaje recibido: {data}')
        socket_io.emit('response', {'data': f'Servidor recibió: {data}'})  # Enviar respuesta al cliente

    # Otro ejemplo para un evento personalizado llamado 'custom_event'
    @socket_io.on('custom_event')
    def handle_custom_event(data):
        print(f'Evento personalizado recibido: {data}')
        socket_io.emit('response', {'data': 'Recibido en custom_event'})