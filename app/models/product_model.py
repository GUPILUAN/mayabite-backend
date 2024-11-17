from app import mongo
from bson import ObjectId
import base64


class Product:
    # Model
    def __init__(
        self, name: str, price: float, description: str, image: bytes, category: str
    ) -> None:
        self.name: str = name
        self.price: float = price
        self.description: str = description
        self.image: bytes = image
        self.category: str = category

    @staticmethod
    def get_all() -> list[dict]:
        # Verifica que exista la base de datos
        if mongo.db is None:
            return []
        products: list = list(mongo.db.products.find())
        for product in products:
            product["_id"] = str(product["_id"])
            image_base64 = base64.b64encode(product["image"]).decode("utf-8")
            product["image"] = image_base64

        return products

    @staticmethod
    def get_one(id: str) -> dict | None:
        # Verifica que exista la base de datos
        if mongo.db is None:
            return
        # Intenta encontrar el producto por el id
        try:
            product_found: dict | None = mongo.db.products.find_one(
                {"_id": ObjectId(id)}
            )
        except:
            product_found = None

        if product_found:
            product_found["_id"] = str(product_found["_id"])
            image_base64 = base64.b64encode(product_found["image"]).decode("utf-8")
            product_found["image"] = image_base64

        return product_found

    @staticmethod
    def add_one(prod: dict) -> bool:
        # Verifica que exista la base de datos
        if mongo.db is None:
            return False
        return mongo.db.products.insert_one(prod).acknowledged

    @staticmethod
    def add_many(prods: dict) -> None:
        # Verifica que exista la base de datos
        if mongo.db is None:
            return

        mongo.db.products.insert_many(prods)

    @staticmethod
    def delete(id: str) -> bool:
        # Verifica que exista la base de datos
        if mongo.db is None:
            return False
        return mongo.db.products.find_one_and_delete({"_id": ObjectId(id)})

    @staticmethod
    def get_all_from(list_: list, field: str | None, order: int | None) -> list[dict]:
        # Verifica que exista la base de datos
        if mongo.db is None:
            return []
        # Intenta encontrar los productos por la lista
        list_ids: list = [ObjectId(product["id"]) for product in list_]
        filter_: dict = {"_id": {"$in": list_ids}}
        if field is None:
            field = "name"
        if order is None:
            order = 1
        products_found: list = list(mongo.db.products.find(filter_).sort(field, order))

        for product in products_found:
            product["_id"] = str(product["_id"])
            image_base64 = base64.b64encode(product["image"]).decode("utf-8")
            product["image"] = image_base64

        return products_found
