from datetime import datetime
import pyotp
from pydantic import BaseModel
import datetime as dt
from typing import Dict, List, Optional
from jose import JWTError, jwt
import db
from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.security import OAuth2, OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from ultils import settings,decode_id,encode_id
#from config import Config
from pydantic import BaseModel
import db
import os


class OAuth2PasswordBearerWithCookie(OAuth2):
    """
    This class is taken directly from FastAPI:
    https://github.com/tiangolo/fastapi/blob/26f725d259c5dbe3654f221e608b14412c6b40da/fastapi/security/oauth2.py#L140-L171
    
    The only change made is that authentication is taken from a cookie
    instead of from the header!
    """
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        # IMPORTANT: this is the line that differs from FastAPI. Here we use 
        # `request.cookies.get(settings.COOKIE_NAME)` instead of 
        # `request.headers.get("Authorization")`
        authorization: str = request.cookies.get(settings.COOKIE_NAME) 
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")





class User(BaseModel):
    id:str
    email:str
    password:str
    created_date:str
    is_two_authentication_enabled:bool
    secret_token:str
    authenticated_by:str
    is_information_validate:bool
    is_validate_email:bool
    role_user:str|None
    is_active:bool
    idinformationuser:str|None
    is_admin:str|None
    getdate:str
    is_authenticated:bool|None
    statuslogin:bool=False
    def get_authentication_setup_uri(self):
        return pyotp.totp.TOTP(self.secret_token).provisioning_uri(
        name=str(self.email), issuer_name=(os.getenv('APP_NAME')))
    
    def is_otp_valid(self, user_otp):
        #totp = pyotp.parse_uri(self.get_authentication_setup_uri())
        totp=pyotp.TOTP(self.secret_token)
        return totp.verify(user_otp)
        #return self.secret_token
    def __repr__(self):
        return f"<user {self.email}>"
    
def create_access_token(data: Dict) -> str:
    to_encode = data.copy()
    expire = dt.datetime.utcnow() + dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt
    
def decode_token(token: str) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Could not validate credentials."
    )
    token = token.removeprefix("Bearer").strip()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        id: str = payload.get("id")
        if id is None:
            raise credentials_exception
    except JWTError as e:
        print(e)
        raise credentials_exception
    
    user = get_user(id)
    return user

def get_current_user_from_token(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current user from the cookies in a request.

    Use this function when you want to lock down a route so that only 
    authenticated users can see access the route.
    """
    user = decode_token(token)
    return user


def get_current_user_from_cookie(request: Request) -> User:
    """
    Get the current user from the cookies in a request.
    
    Use this function from inside other routes to get the current user. Good
    for views that should work for both logged in, and not logged in users.
    """
    token = request.cookies.get(settings.COOKIE_NAME)
    user = decode_token(token)
    return user


def get_user(id:str) -> User:
    id=decode_id(id)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from user_account where id=?"
    value=(id)
    cursor.execute(sql,value)
    user_temp=cursor.fetchone()
    conn.commit()
    conn.close()
    
    if user_temp is not None:
        user=User(id=encode_id(user_temp[0]),email=user_temp[2],password=user_temp[3],created_date=user_temp[4],
                    authenticated_by=user_temp[5],secret_token=user_temp[6],is_two_authentication_enabled=user_temp[7],
                    is_information_validate=user_temp[8],is_validate_email=user_temp[9],role_user=str(user_temp[10]),
                    is_active=user_temp[11],idinformationuser=None,is_admin=None,getdate=str(datetime.now()),is_authenticated=True)
        if user.is_information_validate==True:
            conn=db.connection()
            cursor=conn.cursor()
            sql="select i.id from user_account u join informationUser i on i.id_useraccount=u.id where u.id=?"
            value=(id)
            cursor.execute(sql,value)
            userinfor=cursor.fetchone()
            conn.commit()
            conn.close()
            user.idinformationuser=encode_id(userinfor[0])
        
    else:
        user = User(
            id=0,
            email="",
            password="",
            created_date="",
            authenticated_by="",
            secret_token="",
            is_two_authentication_enabled=False,
            is_information_validate=False,
            is_validate_email=False,
            role_user=None,
            is_active=True,
            idinformationuser=None,
            is_admin=None
            ,getdate=str(datetime.now())
        )
    
    return user


class verifyPassword:
    def __init__(self,email,totp_temp):
        self.email=email
        self.totp_temp=totp_temp
