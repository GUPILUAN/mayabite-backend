from pymongo import ReturnDocument
from app import mongo, bcrypt

class User:
    
    @staticmethod
    def create_user(data : dict) -> tuple[dict,int]:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return {"message":"Internal server error"},500
        #Asegura que todos los campos esten llenos
        try:
            username : str = data["username"]
            email : str = data["email"]
            password : str = data["password"]
        except KeyError as e:
            print("Error:", e)
            return {"message" : "Data error"}, 400
        
        #Verifica que solo los correos que sean de la anahuac puedan registrarse
        valid_email : bool = email.endswith("@anahuac.mx")
        #Verifica que el mismo correo no intente registrarse de nuevo
        email_already_used : bool = mongo.db.users.find_one({"email" : email}) is not None
        if not valid_email:
            return {"message" : "Only anahuac.mx emails are allowed"},400
        if email_already_used:
            return {"message": "email already used"},400
        
        #Si pasa todos los filtros encripta la contraseña
        hashed_password : str = bcrypt.generate_password_hash(password).decode("utf-8")

        new_user : dict = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "is_active": True,
            "confirmed" : False,
            "is_admin": False,
            "is_delivery_man": False,
            "is_working":False
        }

        #Verdadero si se creó con éxito, Falso si hubo algun problema
        user_created : bool = mongo.db.users.insert_one(new_user).acknowledged
        return (new_user,201) if user_created else ({"message" : "Error creating user"},500)
    
    @staticmethod
    def verify_email(email : str | None) -> dict |None:
        #Verifica que exista la base de datos
        if mongo.db is None or email is None:
            return
        #Filtro
        filter_ : dict = {"email": email}
        #Valor que se va a cambiar
        new_value : dict = {"$set": {"confirmed": True}}
        #Regresa None si no encontró nada, regresa el documento actualizado si lo consigue
        updated_doc : dict | None = mongo.db.users.find_one_and_update(
            filter_,
            new_value,
            return_document= ReturnDocument.AFTER
        )
        return updated_doc
    
    @staticmethod
    def login(data : dict) -> tuple[dict,int]:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return {"message":"Internal server error"},500
        #Verifica que los datos necesarios hayan sido ingresados
        try:
            email : str = data["email"]
            password : str = data["password"]
        except KeyError as e:
            print("Error:", e)
            return {"message" : "Data error"}, 400
        
        #Intenta encontrar al usuario
        user : dict | None= mongo.db.users.find_one({"email": email})
        if not user:
            return {"message": "User not found"}, 404
    
        #Si encuentra al usuario verifica que su contraseña sea la correcta 
        # y sólo si esta verificado su email, le permite entrar
        if bcrypt.check_password_hash(user["password"], password):
            if user["confirmed"] == True:
                return {"email" : email},200
            else:
                return {"message" : "Account not confirmed"}, 401
        else:
            return {"message": "Invalid credentials"}, 401
        
    @staticmethod
    def change_password(user_email : str | None, new_password : str | None)->bool:
        #Verifica que exista la base de datos
        if mongo.db  is None or not user_email or not new_password:
            return False
        filter_ : dict = {"email": user_email}
        hashed_password : str = bcrypt.generate_password_hash(new_password).decode("utf-8")
        new_value : dict = {"$set": {"password": hashed_password}}
        updated_doc : dict | None = mongo.db.users.find_one_and_update(
            filter_,
            new_value,
            return_document= ReturnDocument.AFTER
        )
        return updated_doc is not None

class Product:
    @staticmethod
    def get_all() -> list[dict]:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return []
        return list(mongo.db.products.find())
    
    @staticmethod
    def get_one(id : str)-> dict | None:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return
        return mongo.db.products.find_one({"_id": id})
    
    @staticmethod
    def add_one(prod : dict) -> None:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return
        mongo.db.products.insert_one(prod)

    @staticmethod
    def add_many(prods : dict) -> None:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return
        mongo.db.products.insert_many(prods)

    @staticmethod
    def delete(prod) -> None:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return
        mongo.db.products.delete_one(prod)

class Store:
    @staticmethod
    def get_all() -> list[dict]:
        #Verifica que exista la base de datos
        if mongo.db is None:
            return []
        return list(mongo.db.stores.find())
    