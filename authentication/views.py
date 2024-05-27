from .forms import  RegisterForm,TwoFactorForm,LoginForm,ForgotPasswordForm,ChangePasswordForm
from authentication.models import User,verifyPassword
import db
from typing import Dict, List, Optional
import qrcode
from PIL import Image
from io import BytesIO
import base64
import pyotp
from datetime import datetime
from datetime import datetime
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status,Cookie
from .models import create_access_token
from fastapi.security import OAuth2, OAuth2PasswordRequestForm
from ultils import settings,get_b64encoded_qr_image,file_path_default,send_mail,encode_id,decode_id
from authentication.models import get_current_user_from_cookie,get_current_user_from_token
import mysql.connector
import os
import config
from dotenv import load_dotenv

from fastapi.responses import JSONResponse
from globalvariable import is_admin,verify_password,messages,id_useraccount,roleuser,image_path_session,fullname_session
auth = APIRouter()
load_dotenv()
HOME_URL = "/home"
SETUP_2FA_URL = "/setup-2fa"
VERIFY_2FA_URL = "/verify-2fa"
templates = Jinja2Templates(directory="templates")



@auth.get("/register", response_class=HTMLResponse,tags=["authentication"])
def register_get(request: Request):
    try:
        user = get_current_user_from_cookie(request)
    except:
        user = None
    form = RegisterForm(request)
    context = {
        "request": request,
        "form":form,
        "current_user":user
    }
    return templates.TemplateResponse("authentication/register.html", context)


@auth.post("resgisteraccersstoken",tags=["authentication"])
def resgister_for_access_token(response: Response, user: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
    access_token = create_access_token(data={"id":user.id})
    response.set_cookie(
        key=settings.COOKIE_NAME, 
        value=f"Bearer {access_token}", 
        httponly=True
    )  
    return {settings.COOKIE_NAME: access_token, "token_type": "bearer"}

@auth.post("/register",tags=["authentication"], response_class=HTMLResponse)
async def register(request: Request):
    messages=[]
    try:
        user = get_current_user_from_cookie(request)
    except:
        user = None
    if user:
        if user.is_authenticated:
            if user.is_two_authentication_enabled:
                messages=[("info","You are already registered")]
                return RedirectResponse(url=HOME_URL)
            else:
                messages=[("info","You have not enabled 2-Factor Authentication. Please enable first to login")]
                return RedirectResponse(url=SETUP_2FA_URL)
    form = RegisterForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            secret=pyotp.random_base32()
            created_date=datetime.now()
            conn=db.connection()
            cursor=conn.cursor()
            value=(form.email,form.password,created_date,'normal',secret,)
            cursor.execute("CALL register_user(%s, %s, %s, %s, %s, @user_id);",value)
            cursor.execute("SELECT @user_id")
            id_user = cursor.fetchone()
            conn.commit()
            conn.close()
            user=None
            if(id_user[0]!=0):
                user = User(id=encode_id(id_user[0]),email=form.email, password=form.password,
                            created_date=str(created_date),authenticated_by="normal",
                            secret_token=secret,is_two_authentication_enabled=False,is_information_validate=False,
                            is_validate_email=False,role_user=None,is_active=True,idinformationuser=None,is_admin=None,getdate=str(datetime.now()),is_authenticated=True,statuslogin=False)
                response= RedirectResponse(url=SETUP_2FA_URL)
                resgister_for_access_token(response=response, user=user)
                messages=[("success","You are registered. You have to enable 2-Factor Authentication first to login")]
                return response
            else:

                messages=[("errors","email is exist")]
        except HTTPException:

            messages=[("errors","Incorrect Email or Password")]
    else:
        messages=[("errors","please enter email anh password")]
    context={
        "request":request,
        "form":form,
        "messages":messages,
        "current_user":user
    }
    
    return templates.TemplateResponse("authentication/register.html", context)

@auth.post("/setup-2fa",tags=["authentication"], response_class=HTMLResponse)
async def setup_two_factor_auth(request: Request,current_user: User = Depends(get_current_user_from_token)):
    secret = current_user.secret_token
    uri = current_user.get_authentication_setup_uri()
    base64_qr_image = get_b64encoded_qr_image(uri)
    context={
        "request":request,
        "image_path":file_path_default,
        "secret":secret,
        "qr_image":base64_qr_image,
        "current_user":current_user
    }
    return templates.TemplateResponse("authentication/setup-2fa.html",context)

@auth.get("/setup-2fa",tags=["authentication"], response_class=HTMLResponse)
async def setup_two_factor_auth_get(request: Request,current_user: User = Depends(get_current_user_from_token)):
    secret = current_user.secret_token
    uri = current_user.get_authentication_setup_uri()
    base64_qr_image = get_b64encoded_qr_image(uri)
    context={
        "request":request,
        "image_path":file_path_default,
        "secret":secret,
        "qr_image":base64_qr_image,
        "current_user":current_user
    }
    return templates.TemplateResponse("authentication/setup-2fa.html",context)

@auth.get("/verify-2fa",tags=["authentication"], response_class=HTMLResponse)
async def verify_two_factor_auth_get(request: Request,current_user: User = Depends(get_current_user_from_token)):
    form = TwoFactorForm(request)
    context={
        "request":request,
        "form":form,
        "image_path":file_path_default,
        "current_user":current_user
    }
    return templates.TemplateResponse("authentication/verify-2fa.html",context)
@auth.post("/verify-2fa",tags=["authentication"], response_class=HTMLResponse)
async def verify_two_factor_auth(request: Request,current_user: User = Depends(get_current_user_from_token)):
    messages=[]
    form = TwoFactorForm(request)
    # totp=pyotp.TOTP(current_user.secret_token)
    # return str(totp.now())

    await form.load_data()
    if await form.is_valid(): 
        if current_user.is_otp_valid(form.otp):
            current_user.statuslogin=True
            if current_user.is_two_authentication_enabled:
                messages=[("success","2FA verification successful. You are logged in!")]
                if not current_user.is_information_validate:
                    return RedirectResponse("/informationuser")
                if current_user.role_user == None:
                    messages=[("info","waiting for admin assign role")]
                    return RedirectResponse(url="/logout")
                return RedirectResponse(url=HOME_URL)
            else:
                current_user.is_two_authentication_enabled = True
                conn=db.connection()
                cursor=conn.cursor()
                sql="update user_account set enabled_authentication=1 where id=%s"
                value=(decode_id(current_user.id),)
                cursor.execute(sql,value)
                conn.commit()
                conn.close()
                #db.session.commit()
                messages=[("success","2FA setup successful")]
                
                if not current_user.is_information_validate:
                    return RedirectResponse("/informationuser")
                if current_user.role_user == None:
                    messages=[("info","waiting for admin assign role")]
                    return RedirectResponse(url="/")
                return RedirectResponse(url=HOME_URL)
                
        else:
            messages=[("danger","Invalid OTP. Please try again.")]
            return RedirectResponse(url=VERIFY_2FA_URL, status_code=status.HTTP_302_FOUND)
    else:
        if not current_user.is_two_authentication_enabled:
            messages=[("info","You have not enabled 2-Factor Authentication. Please enable it first.")]
    context={
        "request":request,
        "form":form,
        "image_path":file_path_default,
        "messages":messages,
        "current_user":current_user
    }
    return templates.TemplateResponse("authentication/verify-2fa.html",context)



@auth.get("/signin",tags=["authentication"], response_class=HTMLResponse)
async def login_get(request: Request,response:Response):
    try:
        user = get_current_user_from_cookie(request)
    except:
        user = None
    form = LoginForm(request)
    context={
        "request":request,
        "form":form,
        "current_user":user
    }
    return templates.TemplateResponse("authentication/login.html",context)




@auth.post("/signin",tags=["authentication"], response_class=HTMLResponse)
async def login(request: Request):
    try:
        current_user = get_current_user_from_cookie(request)
    except:
        current_user = None
    #session['is_admin']="None"
    
    messages=[]
    # if current_user:
    #     if current_user.is_authenticated:
    #         if current_user.is_two_authentication_enabled:
    #             messages=[("info","You are already logged in.")]
    #             if not current_user.is_information_validate:
    #                 return RedirectResponse(url="/informationuser")
    #             if current_user.role_user == None :
    #                 messages=[("info","waiting for admin assign role")]
                    
    #                 return RedirectResponse(url="/logout")
    #             if current_user.statuslogin:
                    
    #                 return RedirectResponse(url=HOME_URL)    
    #             return RedirectResponse(url="/logout")
    #         else:
    #             messages=[("info","You have not enabled 2-Factor Authentication. Please enable first to login.")]
    #             return RedirectResponse(url=SETUP_2FA_URL)
        
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
      
        conn=db.connection()
        cursor=conn.cursor()
        cursor.execute("CALL login_user(%s, %s, @output)", (form.email, form.password))
        cursor.execute("SELECT @output;")
        id_user =cursor.fetchone()
        conn.commit()
        conn.close()
        if id_user[0]!=0:
            
            conn=db.connection()
            cursor=conn.cursor()
            sql="select * from user_account where id=%s"
            value=(id_user[0],)
            cursor.execute(sql,value)
            user_temp=cursor.fetchone()
            conn.commit()
            conn.close()
            user=User(id=encode_id(int(user_temp[0])),email=user_temp[2],password=user_temp[3],created_date=user_temp[4],
                      authenticated_by=user_temp[5],secret_token=user_temp[6],
                      is_two_authentication_enabled=user_temp[7],is_information_validate=user_temp[8],
                      is_validate_email=user_temp[9],role_user=str(user_temp[10]),is_active=user_temp[11],idinformationuser=None,is_admin=None,getdate=str(datetime.now()),is_authenticated=True,statuslogin=False)
            if user.role_user is None :
                messages=[("info","waiting for admin assign role")]
               
                
                return RedirectResponse(url="/logout")
            if not user.is_active:
                messages=[("info","account is not active")]
                return RedirectResponse(url="/logout")
            response= RedirectResponse(url=HOME_URL )
            #response= RedirectResponse(url=VERIFY_2FA_URL)
            resgister_for_access_token(response=response, user=user)
            if not user.is_two_authentication_enabled:
                messages=[("info","You have not enabled 2-Factor Authentication. Please enable first to login.")]
                return RedirectResponse(url=VERIFY_2FA_URL)
            return response
        # elif not user:
        #     flash("You are not registered. Please register.", "danger")
        else:
            messages=[("danger","Invalid username and/or password.")]
    context={
        "request":request,
        "form":form,
        "current_user":current_user

    }
    return templates.TemplateResponse("authentication/login.html", context)

@auth.get("/forgotpassword",tags=["authentication"], response_class=HTMLResponse )
async def forgotpassword_get(request: Request):
    try:
        current_user = get_current_user_from_cookie(request)
    except:
        current_user = None
    form = ForgotPasswordForm(request)
    context={
        "request":request,
        "form":form,
        "messages":messages.message_array(),
        "current_user":current_user
    }
    return templates.TemplateResponse("authentication/forgotpassword.html",context)
@auth.post("/forgotpassword",tags=["authentication"], response_class=HTMLResponse )
async def forgotpassword(response:Response,request: Request):
    try:
        current_user = get_current_user_from_cookie(request)
    except:
        current_user = None
    messages.categorary=None,
    messages.message=None
    form = ForgotPasswordForm(request)
    await form.load_data()
    if await form.is_valid():
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from informationUser i join user_account u on i.id_useraccount=u.id where i.Email=%s"
        value=(form.email,)
        cursor.execute(sql,value)
        user_temp=cursor.fetchone()
        conn.commit()
        conn.close()
        if user_temp is not None:
            if(user_temp[18]=='normal'):
                secret=pyotp.random_base32()
                totp=pyotp.TOTP(secret)
                verify=verifyPassword(email=form.email,totp_temp=totp.now())
                #session['verify_password']=verify
                response.set_cookie(key="verify_password", value=verify)
                #flash("A confirmation email has been sent via email.", "success")
                messages.categorary="success"
                messages.message="A confirmation email has been sent via email."
                return RedirectResponse(url="/verifypassword",status_code=status.HTTP_302_FOUND)
                #return redirect(url_for("authentication.verifypassword"))
            else:
                #flash("account have not set password")
                messages.categorary="info"
                messages.message="account have not set password"
                return RedirectResponse(url="/logout")
                #return redirect(url_for("authentication.login"))

        else:
            #flash("You have not confirmed your account or have not register, please sign in or register and confirm your account ")
            messages.categorary="warning"
            messages.message="you have not confirmed your account or have not register, please sign in or register and confirm your account "
            return RedirectResponse(url="/startPage")
            #return redirect(url_for("core.startPage"))

    context={
        "request":request,
        "form":form,
        "messages":messages.message_array(),
        "current_user":current_user
    }
    return templates.TemplateResponse("authentication/forgotpassword.html",context)
    #return render_template("authentication/forgotpassword.html",form=form)
@auth.get("/verifypassword",tags=["authentication"], response_class=HTMLResponse)
async def verifypassword_get(request:Request):
    try:
        current_user = get_current_user_from_cookie(request)
    except:
        current_user = None
    #verify_password=session.get('verify_password')
    totp=request.cookies.get("totp")
    email=request.cookies.get("email")
    subject = "this is otp :"
    html=totp
    send_mail(email, subject, html,2)
    form = TwoFactorForm(request)
    context={
        "request":request,
        "form":form,
        "messages":messages.message_array(),
        "current_user":current_user,
        "image_path":request.cookies.get("image_path_session"),
        "fullname":request.cookies.get("fullname_session"),
        "roleuser":request.cookies.get("roleuser"),
    }
    return templates.TemplateResponse("authentication/verify-2fa.html",context)
@auth.post("/verifypassword",tags=["authentication"], response_class=HTMLResponse)
async def verifypassword(response:Response,request:Request):
    try:
        current_user = get_current_user_from_cookie(request)
    except:
        current_user = None
    #verify_password=session.get('verify_password')
    totp=request.cookies.get("totp")
    email=request.cookies.get("email")
    subject = "this is otp :"
    html=totp
    send_mail(email, subject, html,2)
    form = TwoFactorForm(request)
    await form.load_data()
    if await form.is_valid():
        if str(totp)==form.otp:
            if current_user is not None:
                #session['id_useraccount']=current_user.id
                response=RedirectResponse(url="/changepassword",status_code=status.HTTP_302_FOUND)
                response.set_cookie(key="id_useraccount", value=current_user.id)
            else:
                conn=db.connection()
                cursor=conn.cursor()
                sql="select * from informationUser where Email=%s"
                value=(email,)
                cursor.execute(sql,value)
                user_temp=cursor.fetchone()
                conn.commit()
                conn.close()
                #session['id_useraccount']=user_temp[5]
                response=RedirectResponse(url="/changepassword",status_code=status.HTTP_302_FOUND)
                response.set_cookie(key="id_useraccount", value=encode_id(user_temp[5]))
            return response    
            #return redirect(url_for("authentication.changepassword"))
        else:
            messages.categorary="danger"
            messages.message="Invalid OTP. Please try again."
            #("Invalid OTP. Please try again.", "danger")
            return RedirectResponse(url="/verifypassword",status_code=status.HTTP_302_FOUND)
            #return redirect(url_for("authentication.verifypassword"))
    context={
        "request":request,
        "form":form,
        "messages":messages.message_array(),
        "current_user":current_user,
        "image_path":request.cookies.get("image_path_session"),
        "fullname":request.cookies.get("fullname_session"),
        "roleuser":request.cookies.get("roleuser"),
    }
    return templates.TemplateResponse("authentication/verify-2fa.html",context)
    #return render_template("authentication/verify-2fa.html", form=form)

@auth.get("/changepassword",tags=["authentication"],response_class=HTMLResponse)
async def changepassword_get(request:Request):
    try:
        current_user = get_current_user_from_cookie(request)
    except:
        current_user = None
    form=ChangePasswordForm(request)
    
    context={
        "request":request,
        "form":form,
        "messages":messages.message_array(),
        "current_user":current_user,
        "image_path":request.cookies.get("image_path_session"),
        "roleuser":request.cookies.get("roleuser"),
        "fullname":request.cookies.get("fullname_session"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession")
    }
    return templates.TemplateResponse("authentication/changepassword.html",context)

@auth.post("/changepassword",tags=["authentication"],response_class=HTMLResponse)
async def changepassword(request:Request):
    try:
        current_user = get_current_user_from_cookie(request)
    except:
        current_user = None
    #id_user=session.get('id_useraccount')
    id_user=request.cookies.get("id_useraccount")
    id_user=decode_id(id_user)
    form=ChangePasswordForm(request)
    await form.load_data()
    if await form.is_valid():
        conn=db.connection()
        cursor=conn.cursor()
        sql="update user_account set password=%s where id=%s"
        value=(form.password,id_user,)
        cursor.execute(sql,value)
        conn.commit()
        conn.close()
        #flash("change password is success")
        messages.categorary="success"
        messages.message="change password is success"
        if current_user is not None:
            return RedirectResponse(url="/home")
            #return redirect(url_for("core.home"))
        return RedirectResponse(url="/signin")
        #return redirect(url_for("authentication.login"))
    context={
        "request":request,
        "form":form,
        "messages":messages.message_array(),
        "current_user":current_user,
        "image_path":request.cookies.get("image_path_session"),
        "roleuser":request.cookies.get("roleuser"),
        "fullname":request.cookies.get("fullname_session"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession")
    }
    return templates.TemplateResponse("authentication/changepassword.html",context)
    #return render_template("authentication/changepassword.html",form=form)

