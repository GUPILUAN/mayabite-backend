from app import mongo
from bson import ObjectId
from datetime import datetime


class Order:
    # Model
    def __init__(
        self,
        customer: str,
        products: list,
        total: float,
        store: str,
        destiny: dict,
    ) -> None:
        self.customer: str = customer
        self.delivery_man: str | None = None
        self.store: str = store
        self.destiny: dict = destiny
        self.products: list = products
        self.messages: list = []
        self.status: str = "pending"
        self.date: datetime = datetime.now()
        self.total: float = total

    def to_dict(self) -> dict:

        return {
            "customer": self.customer,
            "delivery_man": self.delivery_man,
            "store": self.store,
            "destiny": self.destiny,
            "products": self.products,
            "messages": self.messages,
            "status": self.status,
            "date": self.date,
            "total": self.total,
        }

    @staticmethod
    def get_all_from(id: str, type: str) -> list[dict]:
        if mongo.db is None:
            return []
        filter_: dict = {type: id}
        orders: list = list(mongo.db.orders.find(filter_))
        for order in orders:
            order["_id"] = str(order["_id"])
        return orders

    @staticmethod
    def get_one_order(id: str) -> dict | None:
        if mongo.db is None:
            return
        filter_: dict = {"_id": ObjectId(id)}
        order: dict | None = mongo.db.orders.find_one(filter_)
        if order is not None:
            order["_id"] = str(order["_id"])
        return order

    @staticmethod
    def get_pending() -> list:
        if mongo.db is None:
            return []
        filter_: dict = {"status": "pending"}
        orders: list = list(mongo.db.orders.find(filter_))
        for order in orders:
            order["_id"] = str(order["_id"])

        return orders

    @staticmethod
    def get_orders_active(id: str, type: str) -> list[dict]:
        if mongo.db is None:
            return []
        filter_: dict = {
            type: id,
            "status": {"$in": ["active", "delivering", "pending"]},
        }
        orders: list = list(mongo.db.orders.find(filter_))
        for order in orders:
            order["_id"] = str(order["_id"])
        return orders

    @staticmethod
    def create_order(data: dict) -> str | None:
        if mongo.db is None:
            return
        try:
            order: Order = Order(**data)
            return str(mongo.db.orders.insert_one(order.to_dict()).inserted_id)
        except Exception as e:
            print(f"Error creating order: {e}")
            return

    @staticmethod
    def change_order_status(id: str, status: str) -> bool:
        """Esta funcion te permite cambiar el status de la orden

        Args:
            id (str): id de la orden
            status (str): status a cambiar

        Returns:
            bool: True si pudo cambiarse, False si hubo un error
        """
        if mongo.db is None:
            return False
        try:
            filter_: dict = {"_id": ObjectId(id)}
            update: dict = {"$set": {"status": status}}
            return mongo.db.orders.update_one(filter_, update).acknowledged
        except Exception as e:
            print(f"Error in completing the order: {e}")
            return False

    @staticmethod
    def accept_order(id: str, id_delivery_man: str) -> bool:
        """Esta funcion te permite aceptar una orden
        y cambiar el status a "active"
        y agregar el id del deliveryman a la orden
        Args:
        id (str): id de la orden
        id_Deliveryman (str): id del deliveryman
        Returns:
        bool: True si pudo cambiarse, False si hubo un error
        """
        if mongo.db is None:
            return False
        try:
            filter_: dict = {"_id": ObjectId(id)}
            order: dict | None = mongo.db.orders.find_one(filter_)
            if order is None or order["delivery_man"] is not None:
                return False
            update: dict = {
                "$set": {"status": "active", "delivery_man": id_delivery_man}
            }
            return mongo.db.orders.update_one(filter_, update).acknowledged
        except Exception as e:
            print(f"Error in completing the order: {e}")
            return False

    @staticmethod
    def send_message(idOrder: str, idSender: str, message: str, time: str) -> bool:
        """Esta funcion te permite enviar un mensaje
        Args:
        idOrder (str): id de la orden
        idSender (str): id del usuario que envia el mensaje
        message (str): mensaje a enviar
        Returns:
        bool: True si pudo enviarse, False si hubo un error
        """
        if mongo.db is None:
            return False
        try:
            filter_: dict = {"_id": ObjectId(idOrder)}
            order: dict | None = mongo.db.orders.find_one(filter_)
            if order is None:
                return False
            previous_messages: list[dict] = order["messages"]
            new_message: dict = {
                "sender": idSender,
                "message": message,
                "time": time,
            }
            previous_messages.append(new_message)
            update: dict = {"$set": {"messages": previous_messages}}
            return mongo.db.orders.update_one(filter_, update).acknowledged
        except Exception as e:
            print(f"Error in completing the order: {e}")
            return False
