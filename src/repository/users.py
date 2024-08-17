from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Search for user in db by it's email.

    Args:
        email (str): User email.
        db (Session): Session to retrieve data from DB.

    Returns:
        User: Returns user.
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Create new user in the db.

    Args:
        body (UserModel): Consist of id, username, email, password.
        db (Session): Session to connect to DB.

    Returns:
        User: Details of a created user with additional created_at ans avatar data.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Adds update tocken for user.

    Args:
        user (User): Created user.
        token (str | None): User's refresh token.
        db (Session): Session to connect to DB.
    """
    user.refresh_token = token
    db.commit()

async def confirmed_email(email: str, db: Session) -> None:
    """
    Add info if user is confirmed or not.

    Args:
        email (str): User's email thar got the confirmation mail.
        db (Session): Session to connect to DB.
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()

async def update_avatar(email, url: str, db: Session) -> User:
    """
    Updates the user's avatar.

    Args:
        email (_type_): User's email.
        url (str): Avatar's url.
        db (Session): Session to connect to DB.

    Returns:
        User: _description_
    """

    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
