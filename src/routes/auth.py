from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    Route to generate refresh tokens.

    Args:
        credentials (HTTPAuthorizationCredentials, optional): User credentials. Defaults to Security(security).
        db (Session, optional): Session to connect to DB. Defaults to Depends(get_db).

    Raises:
        HTTPException: HTTP_401_UNAUTHORIZED if invalid refresh token.

    Returns:
        dict: Dict with tokens.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Route for registration in our application.

    Args:
        body (UserModel): _description_
        background_tasks (BackgroundTasks): _description_
        request (Request): _description_
        db (Session, optional): Session to connect to DB. Defaults to Depends(get_db).

    Raises:
        HTTPException: HTTP_409_CONFLICT if account already exists.

    Returns:
        dict: _description_
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}

@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Route for user authentication in our application.

    Args:
        body (OAuth2PasswordRequestForm, optional): Email and password. Defaults to Depends().
        db (Session, optional): Session to connect to DB. Defaults to Depends(get_db).

    Raises:
        HTTPException: HTTP_401_UNAUTHORIZED if Invalid email/Email not confirmed/Invalid password.

    Returns:
        str: Returns a JWT token for user authorization
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Email confirmation. Shows a message if email was confirmed or already exists.
    Shows error message if no such user. 

    Args:
        token (str): JWT access_token
        db (Session, optional): Session to connect to DB. Defaults to Depends(get_db).

    Raises:
        HTTPException: HTTP_400_BAD_REQUEST if Verification error.

    Returns:
        dict: Message response.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}

@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    The function returns a response indicating that the email has been sent for confirmation 
    or email already has been confirmed.


    Args:
        body (RequestEmail): JSON body with the email address.
        background_tasks (BackgroundTasks): Task to the BackgroundTasks background task manager to send an email to the user.
        request (Request): Request to the get the base url.
        db (Session, optional): Session to connect to DB. Defaults to Depends(get_db).

    Returns:
        dict: Message response.
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}
