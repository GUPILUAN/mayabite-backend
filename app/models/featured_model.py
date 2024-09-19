from app import mongo
from bson import ObjectId
import base64

class Featured:
    #Model
    def __init__(self, title : str , description : str, stores: list) -> None:
        self.title : str = title
        self.description : str = description
        self.stores : list = stores
        
    @staticmethod
    def get_all_featured() -> list[dict]:
        if mongo.db is None:
            return []
        featured : list = list(mongo.db.featured.find())
        for feature in featured:
            feature['_id'] = str(feature['_id'])
        return featured
    
    @staticmethod
    def create_feature(data: dict) -> bool:
        if mongo.db is None:
            return False
        try:
            return mongo.db.featured.insert_one(data).acknowledged
        except Exception as e:
            print(f"Error creating feature: {e}")
            return False
        
    @staticmethod
    def setInfo(list_ : list) -> list[dict]:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return []
        #Intenta encontrar las tiendas por la lista
        featured : list = list(mongo.db.featured.find())
        stores_id : list = [store["_id"] for store in list_]
        for f in featured:
            f['_id'] = str(f['_id'])
            f["stores"] = [store for store in list_ if store["_id"] in stores_id]

        return  featured
    