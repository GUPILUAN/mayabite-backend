from app import mongo
from bson import ObjectId

class Product:

    @staticmethod
    def get_all() -> list[dict]:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return []
        products : list = list(mongo.db.products.find())
        for product in products:
            product['_id'] = str(product['_id'])
            
        return products 
    
    @staticmethod
    def get_one(id : str)-> dict | None:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return
        #Intenta encontrar el producto por el id
        try:    
            product_found : dict | None = mongo.db.products.find_one({"_id": ObjectId(id)})
        except:
            product_found = None
    
        if product_found:
            product_found['_id'] = str(product_found['_id'])

        return product_found
    
    @staticmethod
    def add_one(prod : dict) -> bool:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return False
        return mongo.db.products.insert_one(prod).acknowledged

    @staticmethod
    def add_many(prods : dict) -> None:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return
        
        mongo.db.products.insert_many(prods)

    @staticmethod
    def delete(id : str) -> bool:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return False
        return mongo.db.products.find_one_and_delete({"_id": ObjectId(id)})

    @staticmethod
    def get_all_from(list_ : list, field : str, order : int) -> list[dict]:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return []
        #Intenta encontrar los productos por la lista
        list_ids : list = [ObjectId(product["_id"]) for product in list_]
        filter_ : dict = {"_id": {"$in":list_ids}}
        products_found : list = list(mongo.db.products.find(filter_).sort(field, order))

        for product in products_found:
            product['_id'] = str(product['_id'])

        return products_found