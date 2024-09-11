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


class Mail:
    MAIL_SERVER : str | None = os.getenv("MAIL_SERVER") #servicio de mail que se usa en el remitente 
    MAIL_PORT : int = 587 #Puerto seguro
    MAIL_USE_TLS : bool = True
    MAIL : str | None = os.getenv("MAIL") #mail del remitente
    MAIL_PASSWORD : str | None = os.getenv("MAIL_PASSWORD") #password del remitente
    HOST : str | None = os.getenv("HOST")# host de la pagina que redirige al verificar la cuenta

    def __init__(self, receiver : str, token : str, purpose : str, user : str="") -> None:
        if not self.MAIL or not self.MAIL_PASSWORD or not self.MAIL_SERVER: #si no se proporciona servicio, correo o password se cancela
            return
        subject : str = "Verifica tu cuenta" if purpose == "verify" else "Restablecimiento de contraseña"
       
        body : str = self.verification(token,user) if purpose == "verify" else self.reset(token)
        
        message : MIMEMultipart = MIMEMultipart()
        message["From"] = f"No Reply Mayabite <{self.MAIL}>"
        message["To"] = receiver
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))
        server : smtplib.SMTP | None = None
        try:
            server = smtplib.SMTP(self.MAIL_SERVER, self.MAIL_PORT)
            server.starttls()  
            server.login(self.MAIL, self.MAIL_PASSWORD)  

          
            server.sendmail(self.MAIL, receiver, message.as_string())
            print("Correo enviado exitosamente")

        except Exception as e:
            print(f"Error al enviar el correo: {e}")
        finally:
            if server:
                server.quit() 

    def verification(self, token : str, user : str )-> str:
        return f"""
                    <html>
                        <body>
                            <p>BIENVENIDO {user.upper()}.<br>
                            Haz clic en el siguiente enlace para verificar tu cuenta:<br>
                            <a href={self.HOST}/verify/{token}>Click aquí para verificar</a>
                            </p>
                        </body>
                    </html>
                """
    def reset(self,token : str)-> str :
        return f"""
                    <html>
                        <body>
                            <p>RESTABLECER CONTRASEÑA.<br>
                            Haz click aquí:<br>
                            <a href={self.HOST}/reset/{token}>Click aquí para restablecer contraseña</a>
                            </p>
                        </body>
                    </html>
                """
