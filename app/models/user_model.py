from pymongo import ReturnDocument
from app import mongo, bcrypt
from datetime import datetime, timedelta
import pytz
from bson import ObjectId
import re


class User:
    # Model
    def __init__(self, username: str, email: str, password: str, phone: str) -> None:
        mexico_tz = pytz.timezone("America/Mexico_City")
        now = datetime.now(mexico_tz)
        self.username: str = username
        self.email: str = email
        self.password: str = password
        self.phone: str = phone
        self.is_active: bool = True
        self.confirmed_account: bool = False
        self.is_admin: bool = False
        self.is_delivery_man: bool = False
        self.is_working: bool = False
        self.is_banned: bool = False
        self.last_login: datetime | None = None
        self.created_at: datetime = now
        self.payment_card: str | None = None
        self.token: str | None = None

    def to_dict(self) -> dict:

        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "phone": self.phone,
            "is_active": self.is_active,
            "confirmed_account": self.confirmed_account,
            "is_admin": self.is_admin,
            "is_delivery_man": self.is_delivery_man,
            "is_working": self.is_working,
            "is_banned": self.is_banned,
            "last_login": self.last_login,
            "created_at": self.created_at,
            "payment_card": self.payment_card,
            "token": self.token,
        }

    @staticmethod
    def get_user_info(user_id: str) -> dict | None:
        if mongo.db is None:
            return
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
            return user

    @staticmethod
    def get_user_id_by_email(email: str | None) -> str | None:
        if mongo.db is None:
            return None
        user = mongo.db.users.find_one({"email": email})
        if user:
            return str(user["_id"])

    @staticmethod
    def create_user(data: dict) -> tuple[dict, int]:
        # Verifica que exista la base de datos
        if mongo.db is None:
            return {"message": "Internal server error"}, 500
        # Asegura que todos los campos esten llenos
        try:
            username: str = data["username"]
            email: str = data["email"]
            password: str = data["password"]
            phone: str = data["phone"]
        except KeyError as e:
            print("Error:", e)
            return {"message": "Data error"}, 400

        # Verifica que solo los correos que sean de la anahuac puedan registrarse
        # valid_email: bool = email.endswith("@anahuac.mx")
        # if not valid_email:
        #   return {"message": "Only anahuac.mx emails are allowed"}, 400

        email_regex = r"^[^@]+@[^@]+\.[^@]+$"
        if not re.match(email_regex, email):
            return {"message": "Invalid email"}, 400

        # Verifica que el mismo correo no intente registrarse de nuevo
        email_already_used: bool = mongo.db.users.find_one({"email": email}) is not None

        if email_already_used:
            return {"message": "email already used"}, 400

        if len(password) < 8:
            return {"message": "Password must be at least 8 characters long"}, 400
        # Si pasa todos los filtros encripta la contraseña
        hashed_password: str = bcrypt.generate_password_hash(password).decode("utf-8")

        new_user: User = User(username, email, hashed_password, phone)

        user_created: str = mongo.db.users.insert_one(new_user.to_dict()).inserted_id
        return {"_id": user_created, "username": username, "email": email}, 201

    @staticmethod
    def verify_email(id: str | None) -> dict | None:
        # Verifica que exista la base de datos
        if mongo.db is None or id is None:
            return
        # Filtro
        filter_: dict = {"_id": ObjectId(id)}
        # Valor que se va a cambiar
        new_value: dict = {"$set": {"confirmed_account": True}}
        # Regresa None si no encontró nada, regresa el documento actualizado si lo consigue
        updated_doc: dict | None = mongo.db.users.find_one_and_update(
            filter_, new_value, return_document=ReturnDocument.AFTER
        )
        return updated_doc

    @staticmethod
    def login(data: dict) -> tuple[dict, int]:
        # Verifica que exista la base de datos
        if mongo.db is None:
            return {"message": "Internal server error"}, 500
        # Verifica que los datos necesarios hayan sido ingresados
        try:
            email: str = data["email"]
            password: str = data["password"]
        except KeyError as e:
            print("Error:", e)
            return {"message": "Data error"}, 400

        # Intenta encontrar al usuario
        user: dict | None = mongo.db.users.find_one({"email": email})
        if not user:
            return {"message": "User not found"}, 404

        # Si encuentra al usuario verifica que su contraseña sea la correcta
        # y sólo si esta verificado su email, le permite entrar
        if bcrypt.check_password_hash(user["password"], password):
            if user["confirmed_account"] == True:
                filter_: dict = {"email": email}
                mexico_tz = pytz.timezone("America/Mexico_City")
                now = datetime.now(mexico_tz)
                future_time = now + timedelta(seconds=30)
                parameters: dict = (
                    {"last_login": now}
                    if user["last_login"] is not None
                    else {"last_login": future_time}
                )
                new_value: dict = {"$set": parameters}
                mongo.db.users.update_one(filter_, new_value)
                return {"_id": str(user["_id"])}, 200
            else:
                return {"message": "Account not confirmed", "user": user}, 401
        else:
            return {"message": "Invalid credentials"}, 401

    @staticmethod
    def change_password(user_id: str | None, new_password: str | None) -> bool:
        # Verifica que exista la base de datos y demás datos esten
        if not user_id or not new_password or len(new_password) < 8 or mongo.db is None:
            return False
        filter_: dict = {"_id": ObjectId(user_id)}
        hashed_password: str = bcrypt.generate_password_hash(new_password).decode(
            "utf-8"
        )
        new_value: dict = {"$set": {"password": hashed_password}}
        updated_doc: dict | None = mongo.db.users.find_one_and_update(
            filter_, new_value, return_document=ReturnDocument.AFTER
        )
        return updated_doc is not None

    @staticmethod
    def change_status(
        user_id: str | None, new_status: bool, status_to_change: str
    ) -> bool:
        # Verifica que exista la base de datos y demás datos esten
        if not user_id or mongo.db is None:
            return False
        filter_: dict = {"_id": ObjectId(user_id)}
        new_value: dict = {"$set": {status_to_change: new_status}}
        updated_doc: dict | None = mongo.db.users.find_one_and_update(
            filter_, new_value, return_document=ReturnDocument.AFTER
        )
        return updated_doc is not None

    @staticmethod
    def add_payment_method(user_id: str, card: str) -> bool:
        # Verifica que exista la base de datos y demás datos esten
        if not user_id or not card or mongo.db is None:
            return False
        filter_: dict = {"_id": ObjectId(user_id)}
        card_encrypted: str = bcrypt.generate_password_hash(card).decode("utf-8")
        new_value: dict = {"$set": {"payment_card": card}}
        return mongo.db.users.update_one(filter_, new_value).acknowledged

    @staticmethod
    def log_out(user_id: str) -> bool:
        # Verifica que exista la base de datos y demás datos esten
        if not user_id or mongo.db is None:
            return False
        filter_: dict = {"_id": ObjectId(user_id)}
        new_value: dict = {"$set": {"last_login": datetime.now()}}
        return mongo.db.users.update_one(filter_, new_value).acknowledged

    @staticmethod
    def get_workers_active() -> int:
        # Verifica que exista la base de datos y demás datos esten
        if mongo.db is None:
            return 0
        return mongo.db.users.count_documents({"is_working": True})

    @staticmethod
    def get_info(id: str) -> dict | None:
        # Verifica que exista la base de datos y demás datos esten
        if mongo.db is None:
            return

        user: dict | None = mongo.db.users.find_one({"_id": ObjectId(id)})
        if user is None:
            return

        return {"username": user["username"], "phone": user["phone"]}
