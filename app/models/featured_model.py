from app import mongo
from bson import ObjectId

class Featured:
    #Model
    def __init__(self, title : str , description : str, stores: list=[]) -> None:
        self.title : str = title
        self.description : str = description
        self.stores : list = stores

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "stores": self.stores
        }
        
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
            featured : Featured = Featured(**data) 
            return mongo.db.featured.insert_one(featured.to_dict()).acknowledged
        except Exception as e:
            print(f"Error creating feature: {e}")
            return False
        
    @staticmethod
    def set_info_from_stores(list_ : list) -> list[dict]:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return []
        #Intenta encontrar las tiendas por la lista
        featured : list[dict] = list(mongo.db.featured.find())
        filtered_featured : list[dict] = [
            {**f, 
                '_id': str(f['_id']), 
                'stores':[store for store in list_ if store["_id"] in [s["id"] for s in f["stores"]]]
            }
            for f in featured if f["stores"]
        ]
        return  filtered_featured