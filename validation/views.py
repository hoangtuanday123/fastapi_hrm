from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.security import OAuth2, OAuth2PasswordRequestForm
from ultils import send_mail,file_path_default,decode_id,encode_id
from authentication.models import get_current_user_from_cookie,get_current_user_from_token
from .forms import informationUserForm
from authentication.models import User
import db
from itsdangerous import URLSafeTimedSerializer
import os
from jinja2 import Environment,FileSystemLoader,select_autoescape
validate=APIRouter()
templates = Jinja2Templates(directory="templates")

env = Environment(
    loader=FileSystemLoader(searchpath="./templates"),
    autoescape=select_autoescape(['html', 'xml'])
)


@validate.get("/informationuser",response_class=HTMLResponse)
async def informationuser_get(request: Request,current_user: User = Depends(get_current_user_from_token)):
    form = informationUserForm(request)
    context={
        "request":request,
        "form":form,
        "image_path":file_path_default,
        "current_user":current_user
    }
    return templates.TemplateResponse("validation/informationUserValidate.html",context)


@validate.post("/informationuser",response_class=HTMLResponse)
async def informationuser(request: Request,current_user: User = Depends(get_current_user_from_token)):
    messages=[]
    form = informationUserForm(request)
    await form.load_data()
    if await form.is_valid():
        email=""
        if current_user.authenticated_by=="normal" or current_user.authenticated_by=="google":
            email=current_user.email
        else:
            email=form.Email
            current_user.email=email
        
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from informationUser where id_useraccount=?"
        value=(decode_id(current_user.id))
        cursor.execute(sql,value)
        user_temp=cursor.fetchone()
        conn.commit()
        conn.close()
        if user_temp is None:

            conn=db.connection()
            cursor=conn.cursor()
            sql="""SET NOCOUNT ON;
                    insert into informationUser(Fullname,Nickname,Email,Contactaddress,id_useraccount) values(?,?,?,?,?)
                    DECLARE @id int;
                    SET @id = SCOPE_IDENTITY();    
                    insert into latestEmployment(idinformationuser) values (@id)"""
            value=(form.Fullname,form.Nickname,email,form.Contactaddress,decode_id(current_user.id))
            cursor.execute(sql,value)
            conn.commit()
            conn.close()
        token = generate_token(email)
        confirm_url=f"http://localhost:8000/confirm/{token}"  
        #confirm_url= RedirectResponse(url=f"/confirm/{token}")#, _external=True)
        confirm_url_temp={
            "confirm_url":confirm_url,
            "request":request
        }
        #html =templates.TemplateResponse("validation/confirm_email.html",confirm_url_temp)
        template = env.get_template('validation/confirm_email.html',confirm_url_temp)
        html=template.render(confirm_url_temp)
        subject = "Please confirm your email"
        send_mail(email, subject, html,1)
        messages=[("success","A confirmation email has been sent via email.")]
        return RedirectResponse(url="/inactiveEmail")
    context={
        "request":request,
        "form":form,
        "messages":messages,
        "image_path":file_path_default,
        "current_user":current_user
    }
    return templates.TemplateResponse("validation/informationUserValidate.html",context)


@validate.get("/inactiveEmail",response_class=HTMLResponse)
def inactive_get(request: Request,current_user: User = Depends(get_current_user_from_token)):
    if current_user.is_information_validate:
        return RedirectResponse(url="/home")
    context={
        "request":request,
        "image_path":file_path_default,
        "current_user":current_user
    }
    return templates.TemplateResponse("validation/inactiveEmail.html",context)

@validate.post("/inactiveEmail",response_class=HTMLResponse)
def inactive(request: Request,current_user: User = Depends(get_current_user_from_token)):
    if current_user.is_information_validate:
        return RedirectResponse(url="/home")
    context={
        "request":request,
        "image_path":file_path_default,
        "current_user":current_user
    }
    return templates.TemplateResponse("validation/inactiveEmail.html",context)

def generate_token(email):
    serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY') )
    return serializer.dumps(email, salt=os.getenv('SECURITY_PASSWORD_SALT') )

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
    try:
        email = serializer.loads(
            token, salt=os.getenv('SECURITY_PASSWORD_SALT'), max_age=expiration
        )
        return email
    except Exception:
        return False
    
@validate.post("/confirm/{token}",response_class=HTMLResponse)
async def confirm_email(token,request: Request,current_user: User = Depends(get_current_user_from_token)):
    messages=[]
    if current_user.is_information_validate:
        conn=db.connection()
        cursor=conn.cursor()
        sql="select i.id from user_account u join informationUser i on i.id_useraccount=u.id where u.id=?"
        value=(decode_id(current_user.id))
        cursor.execute(sql,value)
        userinfor=cursor.fetchone()
        conn.commit()
        conn.close()
        current_user.idinformationuser=encode_id(userinfor[0])
        messages=[("success","Account already confirmed.")]
        return RedirectResponse(url="/home")
    email = confirm_token(token)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from informationUser where id_useraccount=?"
    value=(decode_id(current_user.id))
    cursor.execute(sql,value)
    information=cursor.fetchone()
    conn.commit()
    conn.close()
    if information[3] == email:
        current_user.is_information_validate = True
        conn=db.connection()
        cursor=conn.cursor()
        sql="update user_account set infor_validate=1 where id=?"
        value=(decode_id(current_user.id))
        cursor.execute(sql,value)
        conn.commit()
        conn.close()

        conn=db.connection()
        cursor=conn.cursor()
        sql="select i.id from user_account u join informationUser i on i.id_useraccount=u.id where u.id=?"
        value=(decode_id(current_user.id))
        cursor.execute(sql,value)
        userinfor=cursor.fetchone()
        conn.commit()
        conn.close()
        current_user.idinformationuser=encode_id(userinfor[0])
        messages=[("success","You have confirmed your account. Thanks!")]
    else:
        messages=[("danger","The confirmation link is invalid or has expired.")]
        return RedirectResponse(url="/informationuser")
    if current_user.role_user == None:
        messages=[("info","waiting for admin assign role")]
        return RedirectResponse(url="/logout")
    return RedirectResponse(url="/home")

@validate.get("/confirm/{token}",response_class=HTMLResponse)
async def confirm_email_get(token,request: Request,current_user: User = Depends(get_current_user_from_token)):
    messages=[]
    if current_user.is_information_validate:
        conn=db.connection()
        cursor=conn.cursor()
        sql="select i.id from user_account u join informationUser i on i.id_useraccount=u.id where u.id=?"
        value=(decode_id(current_user.id))
        cursor.execute(sql,value)
        userinfor=cursor.fetchone()
        conn.commit()
        conn.close()
        current_user.idinformationuser=encode_id(userinfor[0])
        messages=[("success","Account already confirmed.")]
        return RedirectResponse(url="/home")
    email = confirm_token(token)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from informationUser where id_useraccount=?"
    value=(decode_id(current_user.id))
    cursor.execute(sql,value)
    information=cursor.fetchone()
    conn.commit()
    conn.close()
    if information[3] == email:
        current_user.is_information_validate = True
        conn=db.connection()
        cursor=conn.cursor()
        sql="update user_account set infor_validate=1 where id=?"
        value=(decode_id(current_user.id))
        cursor.execute(sql,value)
        conn.commit()
        conn.close()

        conn=db.connection()
        cursor=conn.cursor()
        sql="select i.id from user_account u join informationUser i on i.id_useraccount=u.id where u.id=?"
        value=(decode_id(current_user.id))
        cursor.execute(sql,value)
        userinfor=cursor.fetchone()
        conn.commit()
        conn.close()
        current_user.idinformationuser=encode_id(userinfor[0])
        messages=[("success","You have confirmed your account. Thanks!")]
    else:
        # conn=db.connection()
        # cursor=conn.cursor()
        # sql="update informationUser where id_useraccount=?"
        # value=(current_user.id)
        # cursor.execute(sql,value)
        # conn.commit()
        # conn.close()
        messages=[("danger","The confirmation link is invalid or has expired.")]
        return RedirectResponse(url="/informationuser")
    if current_user.role_user == None:
        messages=[("info","waiting for admin assign role")]
        return RedirectResponse(url="/logout")
    return RedirectResponse(url="/home")

# @validate.route("/resend")
# @login_required
# def resend_confirmation():
#     if current_user.is_information_validate:
#         flash("Your account has already been confirmed.", "success")
#         return redirect(url_for("core.home"))
#     token = generate_token(current_user.email)
#     confirm_url = url_for("validation.confirm_email", token=token, _external=True)
#     html = render_template("validation/confirm_email.html", confirm_url=confirm_url)
#     subject = "Please confirm your email"
#     send_email(current_user.email, subject, html)
#     flash("A new confirmation email has been sent.", "success")
#     return redirect(url_for("validation.inactive"))

