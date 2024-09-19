from app import mongo
from bson import ObjectId

class Category:

    #Model
    def __init__(self, name :str, is_store_category : bool) -> None:
        self.name : str = name
        self.is_store_category : bool = is_store_category


    @staticmethod
    def get_all_categories() -> list[dict]:
        if mongo.db is None:
            return []
        categories : list = list(mongo.db.categories.find())
        for category in categories:
            category['_id'] = str(category['_id'])
        return categories
    
    @staticmethod
    def create_category(data: dict) -> bool:
        if mongo.db is None:
            return False
        try:
            return mongo.db.categories.insert_one(data).acknowledged
        except Exception as e:
            print(f"Error creating category: {e}")
            return False
    
    @staticmethod
    def get_category_stores(boolean : bool) -> list[dict]:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return []
        #Intenta encontrar los productos por la lista
        filter_ : dict = {"is_store_category": boolean}
        categories_found : list = list(mongo.db.categories.find(filter_))

        for category in categories_found:
            category['_id'] = str(category['_id'])

        return categories_found
