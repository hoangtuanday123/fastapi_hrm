from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from authentication.models import get_current_user_from_cookie,get_current_user_from_token
from ultils import settings,encode_id,decode_id
from authentication.models import User
import db
from ultils import file_path_default
from globalvariable import is_admin,roleuser,rolegroup,readrights,writerights,idaccountadminmanager

import pyotp
from authentication.models import verifyPassword
from globalvariable import verify_password,messages
from validation.forms import informationUserForm
core_bp = APIRouter()
templates = Jinja2Templates(directory="templates")
# global variables
_front_cccd= ''
_back_cccd= ''
_image_path = ""#avatar default
_front_healthyInsurance = ""
_back_healthyInsurance =""
_driver_file_url = ""
_attachedFileName = ""
_fullname =""
_roleuser = ""
_roleadmin = ""
_image_path_admin = ""
_fullname_admin = ""


def authorizationUser(current_user: User = Depends(get_current_user_from_token)):
    global _image_path,_fullname,_roleuser,_image_path_admin 
    conn=db.connection()
    cursor=conn.cursor()
    sql="select role_name from role_user where id=?"
    value=(current_user.role_user)
    cursor.execute(sql,value)
    user_role=cursor.fetchone()
    #session['roleuser']=user_role[0]
    roleuser.value=user_role[0]


    cursor1=conn.cursor()
    sql1="select * from informationUser where id_useraccount=?"
    value1=(decode_id(current_user.id))
    cursor1.execute(sql1,value1)
    user_temp=cursor1.fetchone()
    _roleuser=user_role[0]
    
    # set image path
    # found_avatar = user_avatar.find_picture_name_by_id(user_temp[0])
    # if found_avatar and found_avatar[2] != "":
    #     _image_path = found_avatar[2]
    # else:
    #     _image_path = file_path_default
  
    _fullname = user_temp[1]

    #session['rolegroup']=""
    rolegroup.value=""
    #session['readrights']=None
    readrights.value=None
    #session['writerights']=None
    writerights.value=None

    if user_role[0]=="candidate":
        image_path = file_path_default
        fullname = _fullname
        return RedirectResponse(url=f"/candidate/{image_path}/{fullname}")
        #return redirect(url_for("candidate.candidatepage",image_path = _image_path,fullname = _fullname))
    # elif user_role[0]=="employee":
    #     return redirect(url_for("employee.employeepage",image_path = _image_path,fullname = _fullname))
    # elif user_role[0]=="employee_manager":
    #     return redirect(url_for("employeemanager.employeemanagerpage",image_path = _image_path,fullname = _fullname))
    # elif user_role[0]=="client_manager":
    #     return redirect(url_for("clientmanager.clientmanagerpage",image_path = _image_path,fullname = _fullname))
    # elif user_role[0]=="account_manager":
    #     return redirect(url_for("accountmanager.accountmanagerpage",image_path = _image_path,fullname = _fullname))
    # elif user_role[0]=="admin":
        

    #     _roleadmin = "admin"
    #     _roleuser = ""
    #     _image_path_admin = _image_path
       
    #     _fullname_admin = _fullname


    #     #session['writerights']=1
    #     writerights.value=1
    #     return redirect(url_for("admin.adminpage",image_path_admin=_image_path_admin,fullname_admin = _fullname_admin,roleadmin = _roleadmin))
        
    else:
        return "You have not been granted access to the resource"

@core_bp.get("/home")
def home(current_user: User = Depends(get_current_user_from_token)): 
    return authorizationUser(current_user)

@core_bp.post("/home")
def home_get(current_user: User = Depends(get_current_user_from_token)): 
    return authorizationUser(current_user)

@core_bp.get('/')
def index_get():
    return RedirectResponse(url='/startPage')
@core_bp.post('/')
def index():
    return RedirectResponse(url='/startPage')


@core_bp.get("/startPage",response_class=HTMLResponse)
def startPage_get(request: Request):
    try:
        user = get_current_user_from_cookie(request)
    except:
        user = None
    context={"request":request,
             "current_user":user}
    return templates.TemplateResponse("core/startPage.html",context)

@core_bp.post("/startPage",response_class=HTMLResponse)
def startPage(request: Request):
    try:
        user = get_current_user_from_cookie(request)
    except:
        user = None
    context={"request":request,
             "current_user":user}
    return templates.TemplateResponse("core/startPage.html",context)

@core_bp.get("/logout", response_class=HTMLResponse)
def logout_get():
    response = RedirectResponse(url="/")
    response.delete_cookie(settings.COOKIE_NAME)
    return response

@core_bp.post("/logout", response_class=HTMLResponse)
def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie(settings.COOKIE_NAME)
    return response

@core_bp.get("/getcodechangepassword", response_class=HTMLResponse)
def getcodechangepassword_get(request:Request,current_user: User = Depends(get_current_user_from_token)):
        messages.categorary=None
        messages.message=None
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from informationUser i join user_account u on i.id_useraccount=u.id where u.id=?"
        value=(decode_id(current_user.id))
        cursor.execute(sql,value)
        user_temp=cursor.fetchone()
        conn.commit()
        conn.close()
        if(user_temp[18]=='normal'):
            secret=pyotp.random_base32()
            totp=pyotp.TOTP(secret)
            verify=verifyPassword(email=user_temp[15],totp_temp=totp.now())
            #session['verify_password']=verify
            verify_password.value=verify
            messages.categorary="success"
            messages.message="A confirmation email has been sent via email."
            #flash("A confirmation email has been sent via email.", "success")
            return RedirectResponse("/verifypassword")
            #return redirect(url_for("authentication.verifypassword"))
        else:
            messages.categorary="info"
            messages.message="account have not set password"
            #flash("account have not set password")
            return RedirectResponse(url="/startPage")
            #return redirect(url_for("core.startPage"))

@core_bp.post("/getcodechangepassword", response_class=HTMLResponse)
def getcodechangepassword(request:Request,current_user: User = Depends(get_current_user_from_token)):
        messages.categorary=None
        messages.message=None
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from informationUser i join user_account u on i.id_useraccount=u.id where u.id=?"
        value=(decode_id(current_user.id))
        cursor.execute(sql,value)
        user_temp=cursor.fetchone()
        conn.commit()
        conn.close()
        if(user_temp[18]=='normal'):
            secret=pyotp.random_base32()
            totp=pyotp.TOTP(secret)
            verify=verifyPassword(email=user_temp[15],totp_temp=totp.now())
            #session['verify_password']=verify
            verify_password.value=verify
            messages.categorary="success"
            messages.message="A confirmation email has been sent via email."
            #flash("A confirmation email has been sent via email.", "success")
            return RedirectResponse("/verifypassword")
            #return redirect(url_for("authentication.verifypassword"))
        else:
            messages.categorary="info"
            messages.message="account have not set password"
            #flash("account have not set password")
            return RedirectResponse(url="/startPage")
            #return redirect(url_for("core.startPage"))

# user profile page
@core_bp.get('/userinformation/{idaccount}', response_class=HTMLResponse)
def userinformation_get(request:Request,idaccount,current_user: User = Depends(get_current_user_from_token)):
    global _roleuser,_roleadmin,_image_path,_fullname_admin,_fullname,_image_path_admin
    readrights.value=None    
    #session['readrights']=None
    form = informationUserForm(request)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from informationUser where id_useraccount=?"
    value=(decode_id(idaccount))
    cursor.execute(sql,value)
    user_temp=cursor.fetchone()
    conn.commit()
    conn.close()
    if user_temp:
        form.Fullname=user_temp[1]
        form.Nickname=user_temp[2]
        form.Email=user_temp[3]
        form.Contactaddress=user_temp[4]
        form.Phone=user_temp[6]
        form.LinkedIn=user_temp[7]
        form.Years=user_temp[8]
        form.Location = user_temp[9]
        form.Maritalstatus=user_temp[10]
        form.Ethnicgroup=user_temp[11]
        form.Religion=user_temp[12]

        # found_avatar = user_avatar.find_picture_name_by_id(user_temp[0])
        # if found_avatar and found_avatar[2] != "":
        #     _image_path = found_avatar[2]
        # else:
        #     _image_path = file_path_default
        _image_path = file_path_default
    context={
        "request":request,
        "current_user":current_user,
        "form":form,
        "image_path":_image_path,
        "image_path_admin":_image_path,
        "informationuserid":encode_id(str(user_temp[0])),
        "fullname":user_temp[1],
        "roleuser":_roleuser,
        "idaccount":idaccount,
        "readrights":readrights.value,

    }
    return templates.TemplateResponse("core/user_information.html",context)
    

@core_bp.post('/userinformation/{idaccount}', response_class=HTMLResponse)
def userinformation(request:Request,idaccount,current_user: User = Depends(get_current_user_from_token)):
    global _roleuser,_roleadmin,_image_path,_fullname_admin,_fullname,_image_path_admin
    readrights.value=None    
    #session['readrights']=None
    form = informationUserForm(request)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from informationUser where id_useraccount=?"
    value=(decode_id(idaccount))
    cursor.execute(sql,value)
    user_temp=cursor.fetchone()
    conn.commit()
    conn.close()
    if user_temp:
        form.Fullname=user_temp[1]
        form.Nickname=user_temp[2]
        form.Email=user_temp[3]
        form.Contactaddress=user_temp[4]
        form.Phone=user_temp[6]
        form.LinkedIn=user_temp[7]
        form.Years=user_temp[8]
        form.Location = user_temp[9]
        form.Maritalstatus=user_temp[10]
        form.Ethnicgroup=user_temp[11]
        form.Religion=user_temp[12]

        # found_avatar = user_avatar.find_picture_name_by_id(user_temp[0])
        # if found_avatar and found_avatar[2] != "":
        #     _image_path = found_avatar[2]
        # else:
        #     _image_path = file_path_default
        _image_path = file_path_default
    context={
        "request":request,
        "current_user":current_user,
        "form":form,
        "image_path":_image_path,
        "image_path_admin":_image_path,
        "informationuserid":encode_id(str(user_temp[0])),
        "fullname":user_temp[1],
        "roleuser":_roleuser,
        "idaccount":idaccount,
        "readrights":readrights.value,

    }
    return templates.TemplateResponse("core/user_information.html",context)
# edit information user profile
@core_bp.post('/edit_userInformation/{col}/{informationuserid}/{data_col}', response_class=HTMLResponse)
def edit_userInformation(request:Request,col,informationuserid,data_col,current_user: User = Depends(get_current_user_from_token)):
    return str(data_col)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id from informationUser where id_useraccount=?"
    cursor.execute(sql,decode_id(current_user.id))
    verify_user=cursor.fetchone()
    conn.commit()
    conn.close()
    if str(decode_id(informationuserid))==str(verify_user[0]):
        conn= db.connection()
        cursor = conn.cursor()
        sql = f"UPDATE informationUser SET {col} = ? WHERE id= ?"
        new_value = col
        cursor.execute(sql,new_value,decode_id(informationuserid))
        cursor.commit()
        cursor.close()
        idaccount= str(current_user.id)
        return RedirectResponse(f'/userinformation/{idaccount}')
        
    elif readrights.value==1:
        conn= db.connection()
        cursor = conn.cursor()
        sql = f"UPDATE informationUser SET {col} = ? WHERE id= ?"
        new_value = col
        cursor.execute(sql,new_value,decode_id(informationuserid))
        cursor.commit()
        cursor.close()


        
        idaccount= idaccountadminmanager.value
        return RedirectResponse(f'/userinformation/{idaccount}')
        