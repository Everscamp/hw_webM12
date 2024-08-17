from pathlib import Path
import os.path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import settings


# module_dir = Path.cwd()
relative_path = "src\\templates"
module_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

absolute_file_path = os.path.join(module_dir, relative_path)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="Desired Name",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=absolute_file_path,
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Sends the email with a JWT token for email verification to a specified user.

    Args:
        email (EmailStr): User Email
        username (str): User username
        host (str): The host where our application is running
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)

