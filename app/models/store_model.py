from app import mongo
from bson import ObjectId
import base64


class Store:
    # Model
    def __init__(
        self, name: str, location: str, description: str, image: bytes, category: str
    ) -> None:
        self.name: str = name
        self.location: str = location
        self.description: str = description
        self.image: bytes = image
        self.category: str = category
        self.inventory: list = []
        self.score: int = 0
        self.stars: float = 0
        self.reviews: int = 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "location": self.location,
            "description": self.description,
            "image": base64.b64encode(self.image).decode("utf-8"),
            "category": self.category,
            "inventory": self.inventory,
            "score": self.score,
            "stars": self.stars,
            "reviews": self.reviews,
        }

    @staticmethod
    def get_all_stores() -> list[dict]:
        # Verifica que exista la base de datos
        if mongo.db is None:
            return []
        stores: list = list(mongo.db.stores.find())
        for store in stores:
            store["_id"] = str(store["_id"])
            if isinstance(store["image"], bytes):
                image_base64 = base64.b64encode(store["image"]).decode("utf-8")
                store["image"] = image_base64

        return stores

    @staticmethod
    def register_store(data: dict) -> bool:
        # Verifica que exista la base de datos
        if mongo.db is None:
            return False

        # Tipado para documentación
        name: str
        location: str
        description: str
        image: bytes
        category: str
        name, location, description, image, category = data.values()

        # Verifica que el nombre del almacen ya exista
        if mongo.db.stores.find_one({"name": name}):
            return False

        # Crea un nuevo almacen
        new_store: Store = Store(name, location, description, image, category)

        return mongo.db.stores.insert_one(new_store.to_dict()).acknowledged

    @staticmethod
    def get_store_by_id(store_id: str) -> dict | None:
        # Verifica que exista la base de datos
        if mongo.db is None:
            return {}
        store: dict | None = mongo.db.stores.find_one({"_id": ObjectId(store_id)})
        if store:
            store["_id"] = str(store["_id"])
            image_base64 = base64.b64encode(store["image"]).decode("utf-8")
            store["image"] = image_base64

        return store

    @staticmethod
    def get_store_inventory(store_id: str) -> list:
        # Verifica que exista la base de datos
        if mongo.db is None:
            return []
        store: dict | None = mongo.db.stores.find_one({"_id": ObjectId(store_id)})
        if store:
            for product in store["inventory"]:
                product["id"] = str(product["id"])
            return store["inventory"]
        return []

    @staticmethod
    def add__product_inventory(store_id: str, products: list) -> bool:
        # Verifica que exista la base de datos
        if mongo.db is None:
            return False
        try:
            filter_: dict = {"_id": ObjectId(store_id)}
        except:
            return False
        # Verifica que el almacen exista
        store: dict | None = mongo.db.stores.find_one(filter_)
        if store is None:
            return False

        # Crear un conjunto con los IDs de los productos en la inventory
        inventory_ids = {product["id"] for product in store["inventory"]}
        products = [p for p in products if p["id"] not in inventory_ids]

        new_inventory: list = store["inventory"] + products

        updated_doc: bool = mongo.db.stores.update_one(
            filter_,
            {"$set": {"inventory": new_inventory}},
        ).acknowledged

        return updated_doc

    @staticmethod
    def delete_product_inventory(store_id: str, product_ids: list) -> bool:
        # Verifica que exista la base de datos
        if mongo.db is None:
            return False
        filter_: dict = {"_id": ObjectId(store_id)}
        # Verifica que el almacen exista
        store: dict | None = mongo.db.stores.find_one(filter_)
        if store is None:
            return False
        # Valor que se va a cambiar
        new_inventory: list = [
            product
            for product in store["inventory"]
            if product["_id"] not in product_ids
        ]
        updated_doc: bool = mongo.db.stores.update_one(
            filter_,
            {"$set": {"inventory": new_inventory}},
        ).acknowledged

        return updated_doc

    @staticmethod
    def product_inventory(store_id: str, product_ids: list, enable: bool) -> bool:
        # Verifica que exista la base de datos
        if mongo.db is None:
            return False
        filter_: dict = {"_id": ObjectId(store_id)}
        # Verifica que el almacen exista
        store: dict | None = mongo.db.stores.find_one(filter_)
        if store is None:
            return False
        # Valor que se va a cambiar
        product_ids = [product["id"] for product in product_ids]
        for product in store["inventory"]:
            if product["id"] in product_ids:
                product["enabled"] = enable

        updated_doc: bool = mongo.db.stores.update_one(
            filter_,
            {"$set": {"inventory": store["inventory"]}},
        ).acknowledged

        return updated_doc

    @staticmethod
    def get_a_review(id: str, review_score) -> bool:
        # Verifica que exista la base de datos
        if mongo.db is None:
            return False
        filter_: dict = {"_id": ObjectId(id)}
        # Verifica que el almacen exista
        store: dict | None = mongo.db.stores.find_one(filter_)
        if store is None:
            return False
        actual_score: int = store["score"]
        actual_reviews: int = store["reviews"]

        new_score: int = actual_score + review_score
        new_reviews: int = actual_reviews + 1
        new_stars: float = new_score / new_reviews

        # Valor que se va a cambiar
        new_review: dict = {
            "score": new_score,
            "stars": review_score if actual_reviews == 0 else new_stars,
            "reviews": 1 if actual_reviews == 0 else new_reviews,
        }

        return mongo.db.stores.update_one(filter_, {"$set": new_review}).acknowledged
