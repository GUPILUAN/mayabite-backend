from app import mongo, socket_io
import gevent
import atexit
import base64
from bson import ObjectId
from flask_socketio import emit, join_room, leave_room
from app.models.order_model import Order

rooms: dict = {}


@socket_io.on("connect")
def handle_connect():
    print("Cliente conectado")
    socket_io.emit(
        "response_server", {"data": "Conexión exitosa"}
    )  # Enviar respuesta al cliente


# Evento cuando se desconecta un cliente
@socket_io.on("disconnect")
def handle_disconnect():
    print("Cliente desconectado")


# Evento para manejar mensajes desde el cliente
@socket_io.on("message")
def handle_message(data):
    room = data.get("room")
    socket_io.emit(
        "response",
        {"data": data},
        to=room,
    )
    user_id = data.get("sender")
    message = data.get("message")
    time = data.get("time")
    result = Order.send_message(room, user_id, message, time)
    if result:
        print("Mensaje enviado correctamente")
    else:
        print("Error al enviar mensaje")


# Evento de socket para unirse a la conversación
@socket_io.on("joinConversation")
def handle_join(data):
    user_id = data.get("user_id")
    conversation_id = data.get("conversation_id")

    if not user_id or not conversation_id:
        print("Error: user_id o conversation_id faltantes")
        return

    if conversation_id not in rooms:
        rooms[conversation_id] = 0

    join_room(conversation_id)
    rooms[conversation_id] += 1

    socket_io.emit(
        "userStatus",
        {
            "userId": user_id,
            "conversation_id": conversation_id,
            "isInConversation": True,
            "count": rooms[conversation_id],
        },
        to=conversation_id,
    )


@socket_io.on("leaveConversation")
def handle_leave(data):
    user_id = data.get("user_id")
    conversation_id = data.get("conversation_id")

    if conversation_id in rooms:

        rooms[conversation_id] -= 1

        if rooms[conversation_id] == 0:
            del rooms[conversation_id]

    if user_id and conversation_id:
        user_count = rooms.get(conversation_id, 0)
        socket_io.emit(
            "userStatus",
            {
                "userId": user_id,
                "conversation_id": conversation_id,
                "isInConversation": False,
                "count": user_count,
            },
            to=conversation_id,
        )

        leave_room(conversation_id)


@socket_io.on("my_order")
def handle_order_active(idOrder):
    print("Obteniendo pedidos pendientes")

    def order(mongodb, id) -> None:
        filter_ = {"_id": ObjectId(id)}
        order = mongodb.orders.find_one(filter_)
        if order:
            order["_id"] = str(order["_id"])
            order["date"] = order["date"].isoformat()
            data = {"order": order}
            socket_io.emit("handleOrder", data)

    if mongo.db is None or not mongo.cx:
        return

    change_stream = mongo.db.orders.watch()
    for change in change_stream:
        if (
            change["operationType"] == "update"
            and str(change["documentKey"]["_id"]) == idOrder
        ):
            updated_fields = change["updateDescription"]["updatedFields"]
            if "status" in updated_fields and updated_fields["status"] in [
                "active",
                "delivered",
                "collected",
                "pending",
                "canceled",
            ]:
                order(mongo.db, idOrder)

    change_stream.close()


@socket_io.on("send_my_location")
def handle_location(data):
    if "user_id" not in data or "location" not in data:
        print("Datos incompletos")
        return

    print("Obteniendo ubicación")
    user_id = data["user_id"]
    location = data["location"]

    socket_io.emit(
        "delivery_man_location",
        {"userId": user_id, "location": location},
    )


@socket_io.on("active_workers")
def handle_active_workers():
    def escuchar(mongodb) -> None:
        usersActive: int = mongodb.users.count_documents({"is_working": True})
        data = {"usersActive": usersActive}
        socket_io.emit("workers", data)

    if mongo.db is None or not mongo.cx:
        return

    change_stream = mongo.db.users.watch()
    for change in change_stream:
        if change["operationType"] == "update":
            updated_fields = change["updateDescription"]["updatedFields"]
            if "is_working" in updated_fields:
                escuchar(mongo.db)


def handle_get_pending_orders():
    print("Obteniendo pedidos pendientes")

    def orders(mongodb) -> None:
        filter_: dict = {"status": "pending"}
        pending_orders: list = list(mongodb.orders.find(filter_))
        for order in pending_orders:
            order["_id"] = str(order["_id"])
            order["date"] = order["date"].isoformat()
        data: dict = {"orders": pending_orders}
        socket_io.emit("getPendingOrders", data)  # Enviar respuesta al cliente

    if mongo.db is None or not mongo.cx:
        return
    change_stream = mongo.db.orders.watch()
    for change in change_stream:
        if change["operationType"] == "update":
            updated_fields = change["updateDescription"]["updatedFields"]
            if "status" in updated_fields and (
                updated_fields["status"] == "active"
                or updated_fields["status"] == "pending"
                or updated_fields["status"] == "canceled"
            ):
                orders(mongo.db)
        elif change["operationType"] == "insert":
            orders(mongo.db)
    change_stream.close()


gevent.spawn(handle_get_pending_orders)


def watch_collection(collection_name):
    if mongo.db is None or not mongo.cx:
        return

    print(f"Escuchando cambios en la colección {collection_name}...")
    try:
        change_stream = mongo.db[collection_name].watch()
        for change in change_stream:
            singular_name = collection_name.rstrip("s")
            if change["operationType"] == "update":
                updated_fields = change["updateDescription"]["updatedFields"]
                document_id = str(change["documentKey"]["_id"])
                try:
                    updated_fields["image"] = base64.b64encode(
                        updated_fields["image"]
                    ).decode("utf-8")
                except KeyError:
                    print("No hay imagen en la actualizacion")
                finally:
                    print(
                        f"Documento actualizado en {collection_name}, se actualizo: {[updated for updated in updated_fields]}"
                    )
                    socket_io.emit(
                        f"{singular_name}Updated",
                        {"document_id": document_id, "updated_fields": updated_fields},
                    )
            elif change["operationType"] == "insert":
                document_inserted = change["fullDocument"]
                try:
                    document_inserted["image"] = base64.b64encode(
                        document_inserted["image"]
                    ).decode("utf-8")
                    document_inserted["_id"] = str(document_inserted["_id"])
                except KeyError:
                    print("No hay alguna key")
                finally:
                    print(
                        f"Documento insertado en {collection_name}: {document_inserted["_id"]}"
                    )
                    socket_io.emit(f"{singular_name}Inserted", document_inserted)
            elif change["operationType"] == "delete":
                deleted_id = change["documentKey"]["_id"]
                print(f"Documento eliminado en {collection_name}: {deleted_id}")
                socket_io.emit(f"{singular_name}Deleted", {"_id": str(deleted_id)})
        change_stream.close()

    except Exception as e:
        print(f"Error al escuchar cambios en {collection_name}: {e}")


def start_watching_collections():
    collections_to_watch = ["stores", "products", "orders"]  # Lista de colecciones
    for collection in collections_to_watch:
        gevent.spawn(watch_collection, collection)


def close_mongo_connection():
    if mongo.db is not None and mongo.cx:
        print("Cerrando conexión a MongoDB...")
        mongo.cx.close()


atexit.register(close_mongo_connection)
