from app import mongo
from bson import ObjectId
from datetime import datetime

class Order:
    #Model
    def __init__(self, store: str, products: dict, customer: str, delivery_man: str, total_price: float, status: str):
        self.store : str = store
        self.products : dict = products
        self.customer : str = customer
        self.delivery_man : str = delivery_man
        self.total_price : float = total_price
        self.status : str = status

    @staticmethod
    def get_order_by_id(order_id: str) -> tuple[dict,int]:
        if mongo.db is None:
            return {"message":"Internal server error"},500

        order : dict | None = mongo.db.orders.find_one({"_id": ObjectId(order_id)})
        if not order:
            return {"message":"No se encontró la orden"}, 404
        
        order["_id"] = order_id
        return order, 200
    
    @staticmethod
    def get_orders_by_user(user_email: str, is_delivery_man: bool) -> tuple[dict,int]:
        if mongo.db is None:
            return {"message":"Internal server error"},500
        
        user = "customer"
        if is_delivery_man is True:
            user = "delivery_man"
        orders : list = list(mongo.db.orders.find({user: user_email}))
        for order in orders:
            order["_id"] = str(order["_id"])
        return orders, 200
    
    @staticmethod
    def create_order(data: dict) -> tuple[dict, int]:
        if mongo.db is None:
            return {"message":"Internal server error"},500
        
        new_order : dict = {
            "customer" : data["customer"],
            "delivery_man" : data["delivery_man"],
            "store" : data["store"],
            "products" : data["products"],
            "total_price" : data["total_price"],
            "status" : "In process",
            "created_at" : datetime.now(),
            "updated_at" : datetime.now()
        }
        order_created = mongo.db.orders.insert_one(new_order)
        if order_created.acknowledged:
            new_order.update({"_id": str(order_created.inserted_id)})
            return (new_order, 201)
        else:
            ({"message" : "Error al crear la orden"}, 500)
    
    @staticmethod
    def update_status(data: dict) -> bool:
        if mongo.db is None:
            return False
        
        try:
            if data["status"] is None or data["order_id"] is None:
                return False
        except KeyError:
            return False
        
        is_updated : bool = mongo.db.orders.update_one({"_id": ObjectId(data["order_id"])}, 
                                                       {"$set": {"status": data["status"], "updated_at": datetime.now()}}).acknowledged
        return is_updated



