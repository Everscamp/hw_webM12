from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from src.conf.config import settings
import pickle
import redis

from src.database.db import get_db
from src.repository import users as repository_users


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def verify_password(self, plain_password: str, hashed_password: str):
        """
        Checks whether the plaintext password matches the hashed password.

        Args:
            plain_password (str): Password bfore hashing
            hashed_password (str): Exactly what is indicated in the argument name

        Returns:
            bool: depends if the password is exist or correct
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Takes a regular password as an argument 
        and returns a hashed version of the password using the hash method of the pwd_context object.

        Args:
            password (str): Regular password.

        Returns:
            str: Hashed password.
        """
        print(type(self.pwd_context.hash(password)))
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Generates a new access_token by encoding a data dictionary called to_encode in JWT.
        Which will be used to authorize the user to access protected resources.
        If expires_delta is not provided, sets the expiration time to 15 minutes from the current UTC time.

        Args:
            data (dict): A dictionary of data to be encoded into a JWT.
            expires_delta (Optional[float], optional): Time delta to calculate the expiration time by adding it to the current time. 

        Returns:
            str, optional: Encoded access_token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(datetime) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token
 
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        A function to generate a new refresh token. This token is used to renew the current access token when it expires. 
        If expires_delta is not passed, the token will be valid for 7 days.

        Args:
            data (dict): A dictionary of data to be encoded into a JWT.
            expires_delta (Optional[float], optional): The time during which the generated token will be valid. Defaults to None. 

        Returns:
            str: Encoded refresh_token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=7)
        to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        Method decodes the refresh_token refresh token to retrieve the user's email.

        Args:
            refresh_token (str): A created previously refresh token.

        Raises:
            HTTPException: HTTP_401_UNAUTHORIZED if token is expired or invalid.

        Returns:
            str: Email if token is valid.
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        Gets information about the current user from the access token access_token. 
        Authenticate a user by decrypting the access token access_token and checking if the user exists in the database.

        Args:
            token (str, optional): Access token. Defaults to Depends(oauth2_scheme). 
            db (Session, optional): To get user from db. Defaults to Depends(get_db).

        Raises:
            credentials_exception: HTTP_401_UNAUTHORIZED if could not validate credentials.

        Returns:
            User: The User object. <class 'src.database.models.User'>
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception
        user = self.r.get(f"user:{email}")
        if user is None:
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.r.set(f"user:{email}", pickle.dumps(user))
            self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)
        return user
    
    def create_email_token(self, data: dict):
        """
        Сreates an encoded JWT token valid for 7 days
        
        Args:
            data (dict): A dictionary of data to be encoded into a JWT

        Returns:
            str: Encoded token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        Retrieves the user's email from the token

        Args:
            token (str): Encoded token

        Raises:
            HTTPException: HTTP_422_UNPROCESSABLE_ENTITY If token is invalid.

        Returns:
            str: Decoded email
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()
