from app import mongo
from bson import ObjectId

class Category:

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
        
