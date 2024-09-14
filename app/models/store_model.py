from app import mongo
from bson import ObjectId

class Store:
    
    @staticmethod
    def get_all_stores() -> list[dict]:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return []
        stores : list = list(mongo.db.stores.find())
        for store in stores:
            store["_id"] = str(store["_id"])
        return stores
    
    @staticmethod
    def register_store(data : dict) -> bool:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return False
        #Verifica que el nombre del almacen ya exista
        if mongo.db.stores.find_one({"name": data["name"]}):
            return False
        #Crea un nuevo almacen
        new_store : dict = {
            "name": data["name"],
            "location": data["location"],
            "inventory" : []
        }
        return mongo.db.stores.insert_one(new_store).acknowledged
    
    @staticmethod
    def get_store_by_id(store_id : str) -> dict | None:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return {}
        store : dict | None = mongo.db.stores.find_one({"_id": ObjectId(store_id)})
        if store:
            store["_id"] = str(store["_id"])
            
        return store
    
    @staticmethod
    def get_store_inventory(store_id : str) -> list:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return []
        store : dict | None = mongo.db.stores.find_one({"_id": ObjectId(store_id)})
        if store:
            for product in store["inventory"]:
                product["_id"] = str(product["_id"])
            return store["inventory"]
        return []

    @staticmethod
    def add__product_inventory(store_id : str, products : list) -> bool:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return False
        filter_ : dict = {"_id": ObjectId(store_id)}
        #Verifica que el almacen exista
        store : dict | None = mongo.db.stores.find_one(filter_)
        if store is None:
            return False
        #Valor que se va a cambiar
        new_inventory : list = store["inventory"] + products
    
        updated_doc : bool = mongo.db.stores.update_one(
            filter_, 
            {"$set": {"inventory" : new_inventory}},
        ).acknowledged

        return updated_doc
    
    @staticmethod
    def delete_product_inventory(store_id : str, product_ids : list) -> bool:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return False
        filter_ : dict = {"_id": ObjectId(store_id)}
        #Verifica que el almacen exista
        store : dict | None = mongo.db.stores.find_one(filter_)
        if store is None:
            return False
        #Valor que se va a cambiar       
        new_inventory : list = [product for product in store["inventory"] if product["_id"] not in product_ids]
        updated_doc : bool = mongo.db.stores.update_one(
            filter_, 
            {"$set": {"inventory" : new_inventory}},
        ).acknowledged

        return updated_doc
    