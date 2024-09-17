from app import mongo
from bson import ObjectId

class Location:

    @staticmethod
    def get_all_locations() -> list[dict]:
        if mongo.db is None:
            return []
        locations : list = list(mongo.db.locations.find())
        for location in locations:
            location['_id'] = str(location['_id'])
        return locations
    
    @staticmethod
    def create_location(data: dict) -> bool:
        if mongo.db is None:
            return False
        try:
            return mongo.db.locations.insert_one(data).acknowledged
        except Exception as e:
            print(f"Error creating location: {e}")
            return False
        
