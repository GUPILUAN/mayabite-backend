import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
load_dotenv() #importa a las variables de entorno que se encuentran en el .env

class Config:
    MONGO_URI : str | None  = os.getenv("MONGO_URI") #MONGO URI en el .env
    JWT_SECRET_KEY : str | None = os.getenv("JWT_SECRET_KEY") #JWT SECRET KEY en el .env
    BCRYPT_LOG_ROUNDS : int = 12 #salty del JWT
    MAX_CONTENT_LENGTH : int = 16 * 1024 * 1024
    
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Mail:
    MAIL_SERVER : str | None = os.getenv("MAIL_SERVER")  # Servicio de mail que se usa en el remitente 
    MAIL_PORT : int = 587  # Puerto seguro
    MAIL_USE_TLS : bool = True
    MAIL : str | None = os.getenv("MAIL")  # Mail del remitente
    MAIL_PASSWORD : str | None = os.getenv("MAIL_PASSWORD")  # Password del remitente
    HOST : str | None = os.getenv("HOST")  # Host de la página que redirige al verificar la cuenta
    status : str = ""

    def __init__(self, receiver: str, token: str, purpose: str, user: str = "") -> None:
        if not self.MAIL or not self.MAIL_PASSWORD or not self.MAIL_SERVER:  
            return
        
        subject: str = "Verifica tu cuenta" if purpose == "verify" else "Restablecimiento de contraseña"
    
        body_html: str = self.verification(token, user) if purpose == "verify" else self.reset(token)
        body_text: str = f"{user.upper()}, sigue este enlace para {purpose}: {self.HOST}/api/user/{purpose}/{token}"

        message: MIMEMultipart = MIMEMultipart("alternative")
        message["From"] = f"Mayabite Team <{self.MAIL}>"
        message["To"] = receiver
        message["Subject"] = subject

        message.attach(MIMEText(body_text, "plain"))
        message.attach(MIMEText(body_html, "html"))

        server: smtplib.SMTP | None = None
        try:
            server = smtplib.SMTP(self.MAIL_SERVER, self.MAIL_PORT)
            server.starttls()  
            server.login(self.MAIL, self.MAIL_PASSWORD)  
            server.sendmail(self.MAIL, receiver, message.as_string())
            print("Correo enviado exitosamente")
            self.status = "success"

        except Exception as e:
            self.status = "error"
            print(f"Error al enviar el correo: {e}")

        finally:
            if server:
                server.quit()

    def verification(self, token: str, user: str) -> str:
        email_body = f"""
                        <html>
                            <head>
                                <style>
                                    body {{
                                        font-family: Arial, sans-serif;
                                        background-color: #f4f4f4;
                                        color: #333333;
                                        margin: 0;
                                        padding: 20px;
                                    }}
                                    .container {{
                                        background-color: #ffffff;
                                        padding: 20px;
                                        border-radius: 8px;
                                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                                    }}
                                    h1 {{
                                        color: #4CAF50;
                                    }}
                                    p {{
                                        line-height: 1.6;
                                    }}
                                    a {{
                                        color: #ffffff;
                                        background-color: #4CAF50;
                                        padding: 10px 20px;
                                        text-decoration: none;
                                        border-radius: 5px;
                                    }}
                                    a:hover {{
                                        background-color: #45a049;
                                    }}
                                    .footer {{
                                        font-size: 12px;
                                        color: #999999;
                                        margin-top: 20px;
                                    }}
                                </style>
                            </head>
                            <body>
                                <div class="container">
                                    <h1>¡BIENVENIDO, {user.upper()}!</h1>
                                    <p>Gracias por registrarte en nuestro servicio. Para completar el proceso de verificación de tu cuenta, por favor haz clic en el enlace a continuación:</p>
                                    <p><a href="{self.HOST}/api/user/verify/{token}">ENLACE DE VERIFICACIÓN</a></p>
                                    <p>Si no solicitaste esta verificación, puedes ignorar este mensaje de manera segura.</p>
                                    <p class="footer">Este es un correo automático enviado por Mayabite. Por favor, no respondas a este mensaje.</p>
                                </div>
                            </body>
                        </html>
                        """

        return email_body

    def reset(self, token: str) -> str:
        email_body_reset = f"""
                                <html>
                                    <head>
                                        <style>
                                            body {{
                                                font-family: Arial, sans-serif;
                                                background-color: #f4f4f4;
                                                color: #333333;
                                                margin: 0;
                                                padding: 20px;
                                            }}
                                            .container {{
                                                background-color: #ffffff;
                                                padding: 20px;
                                                border-radius: 8px;
                                                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                                            }}
                                            h1 {{
                                                color: #FF5733;
                                            }}
                                            p {{
                                                line-height: 1.6;
                                            }}
                                            a {{
                                                color: #ffffff;
                                                background-color: #FF5733;
                                                padding: 10px 20px;
                                                text-decoration: none;
                                                border-radius: 5px;
                                            }}
                                            a:hover {{
                                                background-color: #e64a19;
                                            }}
                                            .footer {{
                                                font-size: 12px;
                                                color: #999999;
                                                margin-top: 20px;
                                            }}
                                        </style>
                                    </head>
                                    <body>
                                        <div class="container">
                                            <h1>Restablecimiento de Contraseña</h1>
                                            <p>Se ha solicitado el restablecimiento de tu contraseña. Para cambiarla, por favor sigue el enlace a continuación:</p>
                                            <p><a href="{self.HOST}/api/user/reset/{token}">ENLACE PARA CAMBIAR CONTRASEÑA</a></p>
                                            <p>Si no solicitaste este cambio, puedes ignorar este mensaje de manera segura.</p>
                                            <p class="footer">Este es un correo automático enviado por Mayabite. Por favor, no respondas a este mensaje.</p>
                                        </div>
                                    </body>
                                </html>
                                """
        return email_body_reset
