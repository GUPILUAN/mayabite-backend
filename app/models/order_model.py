from app import mongo
from bson import ObjectId
from datetime import datetime

class Order:
    #Model
    def __init__(self, customer : str , delivery_man : str, products : list) -> None:
        self.customer : str = customer
        self.delivery_man : str = delivery_man
        self.products : list = products
        self.status : str = "pending"
        self.date : datetime = datetime.now()
        self.total : float = sum([product["price"] for product in products])


    def to_dict(self) -> dict:
        return {
            "customer" : self.customer,
            "delivery_man" : self.delivery_man,
            "products" : self.products,
            "status" : self.status,
            "date" : self.date,
            "total" : self.total
        }
    
    @staticmethod
    def get_all_from(id: str, type : str) -> list[dict]:
        if mongo.db is None:
            return []
        filter_ : dict = {type : id}
        orders : list = list(mongo.db.orders.find(filter_))
        for order in orders:
            order['_id'] = str(order['_id'])
        return orders
    
    @staticmethod
    def create_order(data: dict) -> bool:
        if mongo.db is None:
            return False
        try:
            order :  Order = Order(**data) 
            return mongo.db.orders.insert_one(order.to_dict()).acknowledged
        except Exception as e:
            print(f"Error creating order: {e}")
            return False
        
    @staticmethod
    def change_order_status(id:str, status : str) -> bool:
        if mongo.db is None:
            return False
        try:
            filter_ : dict = {"_id" : id}
            update : dict = {"$set" : {"status" : status}}
            mongo.db.orders.update_one(filter_, update)
            return True
        except Exception as e:
            print(f"Error in completing the order: {e}")
            return False