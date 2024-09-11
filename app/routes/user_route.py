from app.config.config import Mail
from flask import Blueprint, request, make_response, jsonify, render_template, Response
from flask_jwt_extended import create_access_token, jwt_required, decode_token, get_jwt_identity
from datetime import timedelta
from app.models.models import User

user_bp : Blueprint = Blueprint("user_bp", __name__)

#Registering route
@user_bp.route("/register", methods = ["POST"])
def register() -> tuple[Response,int]: 
    #Se obtiene los datos del body
    data : dict = request.get_json()
    #Crea el usuario en la base de datos
    result : tuple[dict,int] = User.create_user(data)

    #Si no se agrega a la base de datos, no existe email agregaado
    email : str | None = result[0].get("email")

    #Si no existe email agregado, regresa el mensaje y el codigo de error
    if not email:
        return jsonify(result[0]),result[1]
    
    access_token : str = create_access_token(identity=email, expires_delta=False)
    #Crea insancia de mail que envia automaticamente correo de verificación
    username : str = str(result[0].get("username"))
    Mail(email,access_token,"verify", username)
    return jsonify({"message" : "User created successfully, please verify the email"}), result[1]


#Verification route
@user_bp.route("/verify/<token>", methods=["GET"])
def verify_email(token : str) -> tuple[Response,int]:
    #intenta decodificar el token para saber que email se esta verificando.
    try:
        email : str | None = decode_token(token).get("sub")
        user_verified : dict | None = User.verify_email(email)
    except:
        user_verified = None
    finally:
        response : Response =make_response(render_template("index.html", success= user_verified))
        return response,200
        #return (jsonify({"message" : "Account confirmed"}),200) if user_verified else (jsonify({"message" : "Invalid token"}), 400)

#Login route
@user_bp.route("/login", methods=["POST"])
def login() -> tuple[Response,int]:
    #Se obtiene los datos del body
    data : dict = request.get_json()
    #Si el resultado tiene un mensaje significa que hubo un error, de lo contrario arroja el access token
    result : tuple = User.login(data)
    if result[0].get("message"):
        return jsonify(result[0]), result[1]
    access_token : str = create_access_token(identity=result[0].get("email"),expires_delta=timedelta(hours=1))
    #response : Response = make_response(jsonify({"message": "Login succeed"}), 200)
    #response.headers['Authorization'] = f"Bearer {access_token}"
    return jsonify(access_token=access_token),200


@user_bp.route('/reset_request', methods=['GET', 'POST'])
def reset_request() -> str | tuple[Response,int]:
    if request.method == 'POST':
        email = request.form.get("email")
        if not email:
            return jsonify({"error": "El correo es necesario"}), 400
        # Crear el token de acceso con JWT
        reset_token : str = create_access_token(identity=email, expires_delta=timedelta(minutes=5))
        try:
            Mail(email, reset_token, "reset")
        except:
            return render_template("reset.html")
        # Crear la respuesta JSON
        response : Response = make_response(render_template("reset.html", sent = reset_token is not None))
        return response,200
    # Si es una solicitud GET, solo renderizamos el formulario
    return render_template("reset.html")

#reset password view route
@user_bp.route("/reset/<token>", methods=["GET"])
def reset_password_view(token : str) -> str | tuple[Response,int]:
    try:
        email : str | None = decode_token(token).get("sub")
    except:
        return jsonify({"message": "Invalid or expired token"}), 400
    return render_template("reset_password.html",email=email)

#Reset password route
@user_bp.route("/reset_password", methods=["POST"])
def reset_password():
    email: str | None = request.form.get("email")
    password : str | None = request.form.get("new_password")
   
    # Cambiar la contraseña
    result : bool = User.change_password(email, password)

    if result:
        return jsonify({"message": "Password has changed successfully"}), 200
    else:
        return jsonify({"message": "Error changing password"}), 400
    

#Protected route
@user_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected() -> tuple[Response,int]:
    current_user : str = get_jwt_identity()
    return jsonify({'message': f'User {current_user} performed a protected action!'}), 200
