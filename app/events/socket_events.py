from app import mongo, socket_io
import gevent
import atexit
import base64

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

    
def watch_collection(collection_name):
    if mongo.db is None or not mongo.cx:
        return
    
    print(f"Escuchando cambios en la colección {collection_name}...")
    try:
        change_stream = mongo.db[collection_name].watch()
        for change in change_stream:
            singular_name = collection_name.rstrip('s')
            if change['operationType'] == 'update':
                updated_fields = change['updateDescription']['updatedFields']
                document_id = str(change['documentKey']['_id'])
                try:
                    updated_fields["image"] = base64.b64encode(updated_fields["image"]).decode("utf-8")
                except KeyError:
                    print("No hay imagen en la actualizacion")
                finally:
                    print(f"Documento actualizado en {collection_name}: {updated_fields}")
                    socket_io.emit(f'{singular_name}Updated', {
                    "document_id": document_id,
                    "updated_fields": updated_fields
                    })
            elif change['operationType'] == 'insert':
                document_inserted = change["fullDocument"]
                try:
                    document_inserted["image"] = base64.b64encode(document_inserted["image"]).decode("utf-8")
                    document_inserted["_id"] = str(document_inserted["_id"])
                except KeyError:
                    print("No hay alguna key")
                finally:
                    print(f"Documento insertado en {collection_name}: {document_inserted}")
                    socket_io.emit(f'{singular_name}Inserted', document_inserted)
            elif change['operationType'] == 'delete':
                deleted_id = change['documentKey']['_id']
                print(f'Documento eliminado en {collection_name}: {deleted_id}')
                socket_io.emit(f'{singular_name}Deleted', {'_id': str(deleted_id)})
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
