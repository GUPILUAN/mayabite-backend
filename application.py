from flask import Flask
from flask_socketio import SocketIO
from app import create_app

app: Flask

app = create_app()

socket_io: SocketIO = SocketIO(app)

# DEV
#if __name__ == "__main__":
    # Usamos socket_io.run en lugar de app.run() para que maneje WebSockets
 #   socket_io.run(app, debug=True, host="0.0.0.0", port=8080)
    