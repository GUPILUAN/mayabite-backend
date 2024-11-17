from app.config.config import Mail
from flask import Blueprint, request, make_response, jsonify, render_template, Response
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    decode_token,
    jwt_required,
)
from datetime import timedelta
from app.models.user_model import User

user_bp: Blueprint = Blueprint("user_bp", __name__)


# Registering route
@user_bp.route("/api/user/register", methods=["POST"])
def register() -> tuple[Response, int]:
    # Se obtiene los datos del body
    data: dict = request.get_json()
    # Crea el usuario en la base de datos
    result: tuple[dict, int] = User.create_user(data)

    # Si no se agrega a la base de datos, no existe el id
    id: str | None = result[0].get("_id")

    # Si no existe id agregado, regresa el mensaje y el codigo de error
    if not id:
        return jsonify(result[0]), result[1]

    username: str = str(result[0].get("username"))
    email: str = str(result[0].get("email"))
    mail_sent: str = Mail(email, id, "verify", username).status

    match mail_sent:
        case "success":
            return (
                jsonify(
                    {"message": "User created successfully, please verify the email"}
                ),
                result[1],
            )
        case "error":
            return (
                jsonify(
                    {
                        "message": "No se pudo enviar el correo de verificación. Se intentará nuevamente cuando inicies sesión."
                    }
                ),
                400,
            )
        case _:
            return jsonify({"message": "No se identificó que error sucedió"}), 400


# Verification route
@user_bp.route("/api/user/verify/<id>", methods=["GET"])
def verify_email(id: str) -> tuple[Response, int]:
    # intenta decodificar el token para saber que email se esta verificando.
    try:
        user_verified: dict | None = User.verify_email(id)
    except:
        user_verified = None
    finally:
        response: Response = make_response(
            render_template("index.html", success=user_verified)
        )
        return response, 200
        # return (jsonify({"message" : "Account confirmed"}),200) if user_verified else (jsonify({"message" : "Invalid token"}), 400)


# Login route
@user_bp.route("/api/user/login", methods=["POST"])
def login() -> tuple[Response, int]:
    # Se obtiene los datos del body
    data: dict = request.get_json()
    # Si el resultado tiene un mensaje significa que hubo un error, de lo contrario arroja el access token y el refresh token
    result: tuple = User.login(data)
    user: dict | None = result[0].get("user")
    if user:
        mail_status: str = Mail(
            user.get("email"), user.get("token"), "verify", user.get("username")
        ).status
        match mail_status:
            case "success":
                return (
                    jsonify(
                        {
                            "message": "Account is not confirmed, another verification link was sent, please verify the email"
                        }
                    ),
                    400,
                )
            case "error":
                return (
                    jsonify(
                        {"message": "No se pudo enviar el correo de verificación."}
                    ),
                    400,
                )

    if result[0].get("message"):
        return jsonify(result[0]), result[1]

    access_token: str = create_access_token(
        identity=result[0].get("_id"), expires_delta=timedelta(hours=1), fresh=True
    )
    refresh_token: str = create_refresh_token(
        identity=result[0].get("_id"), expires_delta=timedelta(days=7)
    )
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200


@user_bp.route("/api/user/biometrics", methods=["GET"])
@jwt_required()
def get_biometrics_token():
    identity = get_jwt_identity()
    biometrics_token: str | None = create_refresh_token(
        identity=identity, expires_delta=False
    )
    return jsonify(biometrics_token=biometrics_token)


@user_bp.route("/api/user/refresh", methods=["POST"])
@jwt_required(refresh=True, verify_type=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(
        identity=identity, expires_delta=timedelta(hours=1)
    )
    # Solo generar un nuevo refresh token si es necesario
    if request.json:
        new_refresh_token = request.json.get("refresh", False)
        if new_refresh_token:
            refresh_token = create_refresh_token(
                identity=identity, expires_delta=timedelta(days=7)
            )
            return jsonify(access_token=access_token, new_refresh_token=refresh_token)

    return jsonify(access_token=access_token)


@user_bp.route("/api/user/reset_request", methods=["GET", "POST"])
def reset_request() -> str | tuple[Response, int]:
    if request.method == "POST":
        data: dict = request.get_json()
        email: str | None = request.form.get("email") or data.get("email")
        if not email:
            return jsonify({"message": "El correo es necesario"}), 400
        # Crear el token de acceso con JWT
        id: str | None = User.get_user_id_by_email(email)
        if not id:
            return jsonify({"message": "No existe un usuario con ese correo"}), 400

        reset_token: str = create_access_token(
            identity=id, expires_delta=timedelta(minutes=5), fresh=True
        )

        mail_status: str = Mail(email, reset_token, "reset").status
        # Si el correo es enviado correctamente
        if mail_status == "success":
            response_data = {
                "message": "Restablecimiento de contraseña solicitado",
                "status": mail_status,
                "details": "Revisa tu correo para continuar con el proceso.",
            }
            if request.is_json:
                return jsonify(response_data), 200
            return make_response(render_template("reset.html", sent=True)), 200
        else:
            # Si falla el envío de correo
            response_data = {
                "message": "No se pudo mandar el correo de reestablecimiento",
                "status": mail_status,
                "details": "Intenta nuevamente después",
            }
            if request.is_json:
                return jsonify(response_data), 400
            return make_response(render_template("reset.html")), 400

        return response
    # Si es una solicitud GET, solo renderizamos el formulario
    return render_template("reset.html")


# reset password view route
@user_bp.route("/api/user/reset/<token>", methods=["GET"])
def reset_password_view(token) -> str | tuple[Response, int]:
    try:
        jwt_decoded: dict = decode_token(token, allow_expired=False)
        if not jwt_decoded["fresh"]:
            return jsonify({"message": "Token no valido"}), 401
        id_decoded: str = jwt_decoded["sub"]
    except:
        return jsonify({"message": "Token expirado"}), 400

    return render_template("reset_password.html", id=id_decoded)


# Reset password route+
@user_bp.route("/api/user/reset_password", methods=["PATCH", "POST"])
def reset_password():
    id: str | None = request.form.get("id")
    password: str | None = request.form.get("new_password")
    # Cambiar la contraseña
    result: bool = User.change_password(id, password)

    if result:
        return jsonify({"message": "Password has changed successfully"}), 200
    else:
        return jsonify({"message": "Error changing password"}), 400


# Protected route
@user_bp.route("/api/user/protected", methods=["GET"])
@jwt_required()
def protected() -> tuple[Response, int]:
    current_user: str = get_jwt_identity()
    return (
        jsonify({"message": f"User {current_user} performed a protected action!"}),
        200,
    )


# Protected route get_user
@user_bp.route("/api/user", methods=["GET"])
@jwt_required()
def get_user_info() -> tuple[Response, int]:
    current_user_id: str = get_jwt_identity()
    return jsonify(User.get_user_info(current_user_id)), 200


@user_bp.route("/api/user/changepassword", methods=["PUT"])
@jwt_required(refresh=False, verify_type=True)
def change_password() -> tuple[Response, int]:
    data: dict = request.get_json()
    try:
        identity: str = get_jwt_identity()
        password: str = data["password"]
        result: bool = User.change_password(identity, password)
        return jsonify({"message": "Password has changed successfully"}), 200
    except:
        return jsonify({"message": "Token expirado"}), 400


@user_bp.route("/api/user/delivery", methods=["PUT"])
@jwt_required(refresh=False, verify_type=True)
def change_status_delivery() -> tuple[Response, int]:

    try:
        data: dict = request.get_json()
        identity: str = get_jwt_identity()
        result: bool = User.change_status(identity, data["status"], "is_delivery_man")

        return (
            (
                jsonify(
                    {"message": "Status has changed successfully", "success": True}
                ),
                200,
            )
            if result
            else (jsonify({"message": "Nope", "success": False}), 400)
        )
    except:
        return jsonify({"message": "Token expirado"}), 400


@user_bp.route("/api/user/working", methods=["PUT"])
@jwt_required(refresh=False, verify_type=True)
def change_status_working() -> tuple[Response, int]:
    try:
        data: dict = request.get_json()
        identity: str = get_jwt_identity()
        result: bool = User.change_status(identity, data["status"], "is_working")

        return (
            (
                jsonify(
                    {"message": "Status has changed successfully", "success": True}
                ),
                200,
            )
            if result
            else (jsonify({"message": "Nope", "success": False}), 400)
        )
    except:
        return jsonify({"message": "Token expirado"}), 400


# Protected route
@user_bp.route("/api/user/addpayent", methods=["GET", "POST"])
@jwt_required()
def add_payment_method() -> tuple[Response, int] | None:
    pass


@user_bp.route("/api/user/active_workers", methods=["GET"])
@jwt_required()
def active_workers() -> tuple[Response, int] | None:
    count: int = User.get_workers_active()
    return jsonify({"count": count}), 200


@user_bp.route("/api/user/<id>", methods=["GET"])
@jwt_required()
def get_info(id: str) -> tuple[Response, int] | None:
    user: dict | None = User.get_info(id)
    if user is None:
        return jsonify({"message": "User not found"}), 404
    return jsonify(user), 200
