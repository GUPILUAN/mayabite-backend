from flask import Flask
from flask_pymongo import PyMongo
from app.config.config import Config
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS

mongo : PyMongo = PyMongo()
bcrypt : Bcrypt = Bcrypt()
jwt : JWTManager = JWTManager()
cors : CORS = CORS()

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    #Inicializamos CORS
    cors.init_app(app)
    #Inicializamos la conexión con Mongo
    mongo.init_app(app)
    #Inicializamos el encriptador de contraseñas
    bcrypt.init_app(app)
    #Inicializamos el JWT
    jwt.init_app(app)
    
    #Rutas
    from app.routes.user_route import user_bp
    app.register_blueprint(user_bp)
    from app.routes.product_route import product_bp
    app.register_blueprint(product_bp)
    from app.routes.store_route import store_bp
    app.register_blueprint(store_bp)
    from app.routes.category_route import category_bp
    app.register_blueprint(category_bp)
    from app.routes.featured_route import featured_bp
    app.register_blueprint(featured_bp)

    return app
    