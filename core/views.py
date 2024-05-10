from fastapi import APIRouter
import pandas as pd
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from authentication.models import get_current_user_from_cookie,get_current_user_from_token
from ultils import settings,encode_id,decode_id
from authentication.models import User
import db
import os
import re
from PIL import Image
import img2pdf
from .forms import  DriveAPI
from config import Config
from fastapi import UploadFile
import shutil
from werkzeug.utils import secure_filename
from .models import user_cccd,user_avatar,allowed_file,allowed_attachment_file
from ultils import file_path_default
from globalvariable import is_admin,roleuser,rolegroup,readrights,writerights,idaccountadminmanager,image_path_session,fullname_session,id_useraccount,selectionItem,tablesession
from admin.forms import groupuserForm
import pyotp
from authentication.models import verifyPassword
from globalvariable import verify_password,messages,fullname_adminsession,image_path_adminsession,roleadmin,front_cccd_session,back_cccd_session
from .forms import CCCDForm,AvatarForm,HCCForm,EducationForm,QualificationForm,EditForm
from validation.forms import informationUserForm,latestEmploymentForm,usercccdForm
core_bp = APIRouter()
templates = Jinja2Templates(directory="templates")
# global variables
# _front_cccd= ''
# _back_cccd= ''
# image_path_session.value = ""#avatar default
# _front_healthyInsurance = ""
# _back_healthyInsurance =""
# _driver_file_url = ""
# _attachedFileName = ""
# _fullname =""
# _roleuser = ""
# _roleadmin = ""
# image_path_session.value_admin = ""
# fullname_adminsession.value = ""

# @auth.get("/set-cookie/{key}/{value}")
# def set_cookie(response: Response,key,value):
    
#     content = {"message": "cookie set"}
#     #response = JSONResponse(content=content)
#     response.set_cookie(key=key, value=value,httponly=True)
#     return {"message": "Cookie set successfully"}

# @auth.get("/get-cookie/{key}")
# def get_cookie(request: Request,key):
#     # Lấy giá trị của cookie
#     cookies = request.cookies
#     cookie_value = cookies.get(key)
#     return  cookie_value

# @auth.get("/test")
# async def test(request: Request):
#     cookie_value = request.cookies.get("test_admin")
    
#     return str(cookie_value)
@core_bp.get("/authorizationUser",tags=['authentication'])
def authorizationUser(request:Request,response:Response, current_user: User = Depends(get_current_user_from_token)):
    #set cookie 
    # response.set_cookie(key="is_admin", value=None,httponly=True)
    # #response.set_cookie(key="roleuser", value=None,httponly=True)
    # response.set_cookie(key="rolegroup", value=None,httponly=True)
    # response.set_cookie(key="readrights", value=None,httponly=True)
    # response.set_cookie(key="writerights", value=None,httponly=True)
    # response.set_cookie(key="verify_password", value=None,httponly=True)
    # response.set_cookie(key="messages", value=None,httponly=True)
    # response.set_cookie(key="id_useraccount", value=None,httponly=True)
    # response.set_cookie(key="idaccountadminmanager", value=None,httponly=True)
    # response.set_cookie(key="selectionItem", value=None,httponly=True)
    # response.set_cookie(key="tablesession", value=None,httponly=True)
    # response.set_cookie(key="image_path_adminsession", value=None,httponly=True)
    # response.set_cookie(key="fullname_adminsession", value=None,httponly=True)
    # response.set_cookie(key="roleadmin", value=None,httponly=True)
    # response.set_cookie(key="image_path_session", value=None,httponly=True)
    # response.set_cookie(key="fullname_session", value=None,httponly=True)
    # response.set_cookie(key="front_cccd_session", value=None,httponly=True)
    # response.set_cookie(key="back_cccd_session", value=None,httponly=True)


    conn=db.connection()
    cursor=conn.cursor()
    sql="select role_name from role_user where id=?"
    value=(current_user.role_user)
    cursor.execute(sql,value)
    user_role=cursor.fetchone()
    roleuser.value=user_role[0]


    cursor1=conn.cursor()
    sql1="select * from informationUser where id_useraccount=?"
    value1=(decode_id(current_user.id))
    cursor1.execute(sql1,value1)
    user_temp=cursor1.fetchone()
    roleuser.value=user_role[0]
    
    #   set image path
    found_avatar = user_avatar.find_picture_name_by_id(user_temp[0])
    if found_avatar and found_avatar[2] != "":
        #image_path_session.value = found_avatar[2]
        response.set_cookie(key="image_path_session", value=found_avatar[2],httponly=True)
    else:
        #image_path_session.value = file_path_default
        response.set_cookie(key="image_path_session", value=file_path_default,httponly=True)
  
    #fullname_session.value = user_temp[1]
    response.set_cookie(key="fullname_session", value=user_temp[1],httponly=True)
 
    # rolegroup.value=""

    # request.cookies.get("readrights")=None

    # writerights.value=None

    if user_role[0]=="candidate":
        #image_path = image_path_session.value
        response.set_cookie(key="roleuser", value="candidate",httponly=True)
        image_path=request.cookies.get("image_path_session")
        #fullname = fullname_session.value
        fullname=request.cookies.get("fullname_session")
        return RedirectResponse(url=f"/candidate/{image_path}/{fullname}",status_code=status.HTTP_302_FOUND)
        #return redirect(url_for("candidate.candidatepage",image_path = image_path_session.value,fullname = _fullname))
    elif user_role[0]=="employee":
        #return str(request.cookies.get("roleadmin"))
        #roleuser.value="employee"
        #image_path = image_path_session.value
        response.set_cookie(key="roleuser", value="employee",httponly=True)
        
        image_path=request.cookies.get("image_path_session")
        #fullname = fullname_session.value
        fullname=request.cookies.get("fullname_session")
        return RedirectResponse(url=f"/employeepage/{image_path}/{fullname}",status_code=status.HTTP_302_FOUND)

    # elif user_role[0]=="employee_manager":
    #     return redirect(url_for("employeemanager.employeemanagerpage",image_path = image_path_session.value,fullname = _fullname))
    # elif user_role[0]=="client_manager":
    #     return redirect(url_for("clientmanager.clientmanagerpage",image_path = image_path_session.value,fullname = _fullname))
    # elif user_role[0]=="account_manager":
    #     return redirect(url_for("accountmanager.accountmanagerpage",image_path = image_path_session.value,fullname = _fullname))
    elif user_role[0]=="admin":
        #roleadmin.value = "admin"
        response.set_cookie(key="roleadmin", value="admin",httponly=True)
        #roleuser.value = ""
        #image_path_adminsession.value = image_path_session.value
        image_path_session=request.cookies.get("image_path_session")
        response.set_cookie(key="image_path_adminsession", value=image_path_session,httponly=True)
        #fullname_adminsession.value = fullname_session.value
        fullname_session=request.cookies.get("fullname_session")
        response.set_cookie(key="fullname_adminsession", value=fullname_session,httponly=True)
      
        #writerights.value=1
        response.set_cookie(key="writerights", value=1,httponly=True)
        #request.cookies.get("readrights")=4
        response.set_cookie(key="readrights", value=4,httponly=True)
        #image_path_admin=image_path_adminsession.value
        image_path_admin=request.cookies.get("image_path_adminsession")
        #fullname_admin = fullname_adminsession.value
        fullname_admin=request.cookies.get("fullname_adminsession")
        return RedirectResponse(url=f'/adminpage/{image_path_admin}/{fullname_admin}')
    else:
        return "You have not been granted access to the resource"

@core_bp.get("/home",tags=['user'])
def home(request:Request,response:Response,current_user: User = Depends(get_current_user_from_token)): 
    #return authorizationUser(request,response,current_user)
    return RedirectResponse(url="/authorizationUser",status_code=status.HTTP_302_FOUND)

@core_bp.post("/home",tags=['user'])
def home_get(request:Request,response:Response,current_user: User = Depends(get_current_user_from_token)): 
    return RedirectResponse(url="/authorizationUser",status_code=status.HTTP_302_FOUND)

@core_bp.get('/',tags=['user'])
def index_get():
    return RedirectResponse(url='/signin')
@core_bp.post('/',tags=['user'])
def index():
    return RedirectResponse(url='/signin')


@core_bp.get("/startPage",tags=['user'],response_class=HTMLResponse)
def startPage_get(request: Request):
    try:
        user = get_current_user_from_cookie(request)
    except:
        user = None
    context={"request":request,
             "current_user":user}
    return templates.TemplateResponse("core/startPage.html",context)

@core_bp.post("/startPage",tags=['user'],response_class=HTMLResponse)
def startPage(request: Request):
    try:
        user = get_current_user_from_cookie(request)
    except:
        user = None
    context={"request":request,
             "current_user":user}
    return templates.TemplateResponse("core/startPage.html",context)

@core_bp.get("/logout",tags=['user'], response_class=HTMLResponse)
def logout_get():
    response = RedirectResponse(url="/")
    response.delete_cookie(settings.COOKIE_NAME)
    # is_admin.value=None
    # roleuser.value=None
    # rolegroup.value=None
    # request.cookies.get("readrights")=None
    # writerights.value=None
    # verify_password.value=None
    # messages.data=None
    # id_useraccount.value=None
    # request.cookies.get("idaccountadminmanager")=None
    # selectionItem.value=None
    # tablesession.value=None
    # image_path_adminsession.value=None
    # fullname_adminsession.value=None
    # roleadmin.value=None
    # image_path_session.value=None
    # fullname_session.value=None
    # front_cccd_session.value=None
    # back_cccd_session.value=None
    return response

@core_bp.post("/logout",tags=['user'], response_class=HTMLResponse)
def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie(settings.COOKIE_NAME)
    # is_admin.value=None
    # roleuser.value=None
    # rolegroup.value=None
    # request.cookies.get("readrights")=None
    # writerights.value=None
    # verify_password.value=None
    # messages.data=None
    # id_useraccount.value=None
    # request.cookies.get("idaccountadminmanager")=None
    # selectionItem.value=None
    # tablesession.value=None
    # image_path_adminsession.value=None
    # fullname_adminsession.value=None
    # roleadmin.value=None
    # image_path_session.value=None
    # fullname_session.value=None
    # front_cccd_session.value=None
    # back_cccd_session.value=None
    return response

@core_bp.get("/getcodechangepassword",tags=['authentication'], response_class=HTMLResponse)
def getcodechangepassword_get(response:Response,request:Request,current_user: User = Depends(get_current_user_from_token)):
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
            #verify_password.value=verify
            response.set_cookie(key="verify_password", value=verify,httponly=True)
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

@core_bp.post("/getcodechangepassword",tags=['authentication'], response_class=HTMLResponse)
def getcodechangepassword(response:Response,request:Request,current_user: User = Depends(get_current_user_from_token)):
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
            #verify_password.value=verify
            response.set_cookie(key="verify_password", value=verify,httponly=True)
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
@core_bp.get('/userinformation/{idaccount}',tags=['user'], response_class=HTMLResponse)
def userinformation_get(response:Response,request:Request,idaccount,current_user: User = Depends(get_current_user_from_token)):
    
    #request.cookies.get("readrights")=None    
    #session['readrights']=None
    form = informationUserForm(request)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select i.*, r.role_name from informationUser i, role_user r, user_account u where  i.id_useraccount= ? and i.id_useraccount=u.id and u.role_id = r.id"
    print("id is:" + str(idaccount))
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

        found_avatar = user_avatar.find_picture_name_by_id(user_temp[0])
        if found_avatar and found_avatar[2] != "":
            response.set_cookie(key="image_path_session", value=found_avatar[2],httponly=True)
            #image_path_session.value = found_avatar[2]
        else:
            #image_path_session.value = file_path_default
            response.set_cookie(key="image_path_session", value=file_path_default,httponly=True)
        if request.cookies.get("roleadmin") == "admin" and request.cookies.get("roleuser") != "admin":
            #roleuser.value = user_temp[13]
            response.set_cookie(key="roleuser", value=user_temp[13],httponly=True)
            #request.cookies.get("idaccountadminmanager") = idaccount
            response.set_cookie(key="idaccountadminmanager", value=idaccount,httponly=True)
    
    context={
        "request":request,
        "current_user":current_user,
        "form":form,
        "image_path":request.cookies.get("image_path_session"),
        "informationuserid":encode_id(str(user_temp[0])),
        "fullname":user_temp[1],
        "roleuser":request.cookies.get("roleuser"),
        "idaccount":idaccount,
        "readrights":request.cookies.get("readrights"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession")

    }
    return templates.TemplateResponse("core/user_information.html",context)
    

@core_bp.post('/userinformation/{idaccount}',tags=['user'], response_class=HTMLResponse)
def userinformation(response:Response,request:Request,idaccount,current_user: User = Depends(get_current_user_from_token)):
  
    #request.cookies.get("readrights")=None    
    #session['readrights']=None
    form = informationUserForm(request)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select i.*, r.role_name from informationUser i, role_user r, user_account u where  i.id_useraccount= ? and i.id_useraccount=u.id and u.role_id = r.id"
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

        found_avatar = user_avatar.find_picture_name_by_id(user_temp[0])
        if found_avatar and found_avatar[2] != "":
            response.set_cookie(key="image_path_session", value=found_avatar[2],httponly=True)
            #image_path_session.value = found_avatar[2]
        else:
            #image_path_session.value = file_path_default
            response.set_cookie(key="image_path_session", value=file_path_default,httponly=True)
        if request.cookies.get("roleadmin") == "admin" and request.cookies.get("roleuser") != "admin":
            #roleuser.value = user_temp[13]
            response.set_cookie(key="roleuser", value=user_temp[13],httponly=True)
            #request.cookies.get("idaccountadminmanager") = idaccount
            response.set_cookie(key="idaccountadminmanager", value=idaccount,httponly=True)


    context={
        "request":request,
        "current_user":current_user,
        "form":form,
        "image_path":request.cookies.get("image_path_session"),
        "informationuserid":encode_id(str(user_temp[0])),
        "fullname":user_temp[1],
        "roleuser":request.cookies.get("roleuser"),
        "idaccount":idaccount,
        "readrights":request.cookies.get("readrights"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession")

    }
    return templates.TemplateResponse("core/user_information.html",context)
# edit information user profile
@core_bp.post('/edit_userInformation/{col}/{informationuserid}',tags=['user'], response_class=HTMLResponse)
async def edit_userInformation(request:Request,col,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id from informationUser where id_useraccount=?"
    cursor.execute(sql,decode_id(current_user.id))
    verify_user=cursor.fetchone()
    conn.commit()
    conn.close()
    form = EditForm(request,col)
    await form.load_data(col)
    if str(decode_id(informationuserid))==str(verify_user[0]):
        conn= db.connection()
        cursor = conn.cursor()
        sql = f"UPDATE informationUser SET {col} = ? WHERE id= ?"
        new_value = getattr(form, col)
        cursor.execute(sql,new_value,decode_id(informationuserid))
        cursor.commit()
        cursor.close()
        idaccount= str(current_user.id)
        return RedirectResponse(f'/userinformation/{idaccount}')
        
    elif request.cookies.get("readrights")==4:
        conn= db.connection()
        cursor = conn.cursor()
        sql = f"UPDATE informationUser SET {col} = ? WHERE id= ?"
        new_value = getattr(form, col)
        cursor.execute(sql,new_value,decode_id(informationuserid))
        cursor.commit()
        cursor.close()
        idaccount= request.cookies.get("idaccountadminmanager")
        return RedirectResponse(f'/userinformation/{idaccount}')
    #return "hello"
@core_bp.get('/groupuserpage/{idinformationuser}',tags=['user'], response_class=HTMLResponse)
def groupuserpage(request: Request,idinformationuser,current_user: User = Depends(get_current_user_from_token)):
    #return idinformationuser
    conn=db.connection()
    cursor=conn.cursor()
    sql="""select g.*,r.rolename from groupuser g join groupuserdetail gd on g.id=gd.idgroupuser join informationUser i
    on i.id=gd.iduser join rolegroupuser r on r.id=gd.idrolegroupuser where i.id=?"""
    value=(str(decode_id(idinformationuser)))
    cursor.execute(sql,value)
    grouptemp=cursor.fetchall()
    conn.commit()
    conn.close()
    groups=[(group[0],group[1],group[2],group[8]) for group in grouptemp]
    form =groupuserForm(request)
    context={
        "request":request,
        "current_user":current_user,
        "groups":groups,
        "image_path":request.cookies.get("image_path_session"),
        "roleuser":request.cookies.get("roleuser"),
        "form":form,
        "fullname":request.cookies.get("fullname_session")
    }
    return templates.TemplateResponse("admin/groupuserpage.html",context)

@core_bp.get('/latestEmployment/{informationuserid}',tags=['user'], response_class=HTMLResponse)
def latestEmployment_get(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
        
        form = latestEmploymentForm(request)
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from latestEmployment where idinformationuser=?"
        cursor.execute(sql,decode_id(informationuserid))
        user_temp=cursor.fetchone()
        conn.commit()
        conn.close()
        if user_temp:
            form.Employer=user_temp[1]
            form.JobTitle=user_temp[2]
            print("job Title get is: " + str(user_temp[2]))
            form.AnnualSalary=user_temp[3]
            form.AnnualBonus=user_temp[4]
            form.RetentionBonus=user_temp[5]
            form.RetentionBonusExpiredDate=user_temp[6]
            form.StockOption=user_temp[7]
            form.StartDate = user_temp[8]
            form.EndDate=user_temp[9]
        idaccount=current_user.id
        
        if request.cookies.get("roleadmin") == "admin" and request.cookies.get("roleuser") != "admin" :
            
            idaccount=request.cookies.get("idaccountadminmanager")
        
        
        context={
        "request":request,
        "current_user":current_user,
        "image_path":request.cookies.get("image_path_session"),
        "roleuser":request.cookies.get("roleuser"),
        "form":form,
        "fullname":request.cookies.get("fullname_session"),
        "informationuserid":informationuserid,
        "idaccount":idaccount,
        "readrights":request.cookies.get("readrights"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession")
        } 
        return templates.TemplateResponse("core/latestEmployment.html",context)

@core_bp.post('/latestEmployment/{informationuserid}',tags=['user'], response_class=HTMLResponse)

def latestEmployment(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
        
        form = latestEmploymentForm(request)
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from latestEmployment where idinformationuser=?"
        cursor.execute(sql,decode_id(informationuserid))
        user_temp=cursor.fetchone()
        conn.commit()
        conn.close()
        if user_temp:
            form.Employer=user_temp[1]
            form.JobTittle=user_temp[2]
            form.AnnualSalary=user_temp[3]
            form.AnnualBonus=user_temp[4]
            form.RetentionBonus=user_temp[5]
            form.RetentionBonusExpiredDate=user_temp[6]
            form.StockOption=user_temp[7]
            form.StartDate = user_temp[8]
            form.EndDate=user_temp[9]
        idaccount=current_user.id
        if request.cookies.get("roleadmin") == "admin" and request.cookies.get("roleuser") != "admin" :
            
            idaccount=request.cookies.get("idaccountadminmanager")
        context={
        "request":request,
        "current_user":current_user,
        "image_path":request.cookies.get("image_path_session"),
        "roleuser":request.cookies.get("roleuser"),
        "form":form,
        "fullname":request.cookies.get("fullname_session"),
        "informationuserid":informationuserid,
        "idaccount":idaccount,
        "readrights":request.cookies.get("readrights"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession")
        }
        return templates.TemplateResponse("core/latestEmployment.html",context)

@core_bp.get('/usercccd/{informationuserid}',tags=['user'], response_class=HTMLResponse)
def usercccd_get(response:Response,request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    
    form = usercccdForm(request)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from information_cccd where idinformationuser=?"
    cursor.execute(sql,decode_id(informationuserid))
    user_temp=cursor.fetchone()
    conn.commit()
    conn.close()
    if user_temp:
        form.No=user_temp[1]
        form.FullName=user_temp[2]
        form.DateOfbirth=user_temp[3]
        form.PlaceOfBirth=user_temp[4]
        form.Address=user_temp[5]
        form.IssueOn=user_temp[6]

    found_cccd = user_cccd.find_picture_name_by_id(decode_id(informationuserid))

    if found_cccd and found_cccd[2] != "":
        #front_cccd_session.value = found_cccd[2]
        response.set_cookie(key="front_cccd_session", value=found_cccd[2],httponly=True)
    else:
        #front_cccd_session.value = ""
        response.set_cookie(key="front_cccd_session", value="",httponly=True)

    if found_cccd and found_cccd[3] != "":
        #back_cccd_session.value = found_cccd[3]
        response.set_cookie(key="back_cccd_session", value=found_cccd[3],httponly=True)

    else:
        #back_cccd_session.value_cccd = ""
        response.set_cookie(key="back_cccd_session", value="",httponly=True)
    idaccount=current_user.id
    if request.cookies.get("roleadmin") == "admin" and request.cookies.get("roleuser") != "admin" :
            
        idaccount=request.cookies.get("idaccountadminmanager")
    context={
        "request":request,
        "current_user":current_user,
        "image_path":request.cookies.get("image_path_session"),
        "roleuser":request.cookies.get("roleuser"),
        "form":form,
        "fullname":request.cookies.get("fullname_session"),
        "informationuserid":informationuserid,
        "front_cccd":request.cookies.get("front_cccd_session"),
        "back_cccd":request.cookies.get("back_cccd_session"),
        "idaccount":idaccount,
        "readrights":request.cookies.get("readrights"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession"),
        "idinformationuser":informationuserid
    }
    return templates.TemplateResponse("core/user_cccd.html",context)
@core_bp.post('/usercccd/{informationuserid}',tags=['user'], response_class=HTMLResponse)
def usercccd(response:Response,request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    
    form = usercccdForm(request)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from information_cccd where idinformationuser=?"
    cursor.execute(sql,decode_id(informationuserid))
    user_temp=cursor.fetchone()
    conn.commit()
    conn.close()
    if user_temp:
        form.No=user_temp[1]
        form.FullName=user_temp[2]
        form.DateOfbirth=user_temp[3]
        form.PlaceOfBirth=user_temp[4]
        form.Address=user_temp[5]
        form.IssueOn=user_temp[6]

    found_cccd = user_cccd.find_picture_name_by_id(decode_id(informationuserid))

    if found_cccd and found_cccd[2] != "":
        #front_cccd_session.value = found_cccd[2]
        response.set_cookie(key="front_cccd_session", value=found_cccd[2],httponly=True)
    else:
        #front_cccd_session.value = ""
        response.set_cookie(key="front_cccd_session", value="",httponly=True)

    if found_cccd and found_cccd[3] != "":
        #back_cccd_session.value = found_cccd[3]
        response.set_cookie(key="back_cccd_session", value=found_cccd[3],httponly=True)

    else:
        #back_cccd_session.value_cccd = ""
        response.set_cookie(key="back_cccd_session", value="",httponly=True)
    idaccount=current_user.id
    if request.cookies.get("roleadmin") == "admin" and request.cookies.get("roleuser") != "admin" :
            
        idaccount=request.cookies.get("idaccountadminmanager")
    context={
        "request":request,
        "current_user":current_user,
        "image_path":request.cookies.get("image_path_session"),
        "roleuser":request.cookies.get("roleuser"),
        "form":form,
        "fullname":request.cookies.get("fullname_session"),
        "informationuserid":informationuserid,
        "front_cccd":request.cookies.get("front_cccd_session"),
        "back_cccd":request.cookies.get("back_cccd_session"),
        "idaccount":idaccount,
        "readrights":request.cookies.get("readrights"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession"),
        "idinformationuser":informationuserid
    }
    return templates.TemplateResponse("core/user_cccd.html",context)
    

@core_bp.get('/healthCheckCertificates/{informationuserid}',tags=['user'],response_class=HTMLResponse)

def healthCheckCertificates_get(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):

    conn = db.connection()
    cursor = conn.cursor()
    sql = "SELECT * from healthCheckCertificates where idinformationuser = ?"
    cursor.execute(sql,decode_id(informationuserid))
    temp = cursor.fetchall()
    df = pd.DataFrame()
    for record in temp:
        df2 = pd.DataFrame(list(record)).T
        df = pd.concat([df,df2])
    conn.close()
    idaccount=current_user.id
    if request.cookies.get("roleadmin") == "admin" and request.cookies.get("roleuser") != "admin" :
            
        idaccount=request.cookies.get("idaccountadminmanager")
    context={
        "request":request,
        "current_user":current_user,
        "image_path":request.cookies.get("image_path_session"),
        "roleuser":request.cookies.get("roleuser"),
        "fullname":request.cookies.get("fullname_session"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession"),
        "informationuserid":informationuserid,
        "temp":temp,
        "idaccount":idaccount,
        "readrights":request.cookies.get("readrights")
    }    
    return templates.TemplateResponse("core/healthCheckCertificates.html",context)
@core_bp.post('/healthCheckCertificates/{informationuserid}',tags=['user'],response_class=HTMLResponse)

def healthCheckCertificates(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):

    conn = db.connection()
    cursor = conn.cursor()
    sql = "SELECT * from healthCheckCertificates where idinformationuser = ?"
    cursor.execute(sql,decode_id(informationuserid))
    temp = cursor.fetchall()
    df = pd.DataFrame()
    for record in temp:
        df2 = pd.DataFrame(list(record)).T
        df = pd.concat([df,df2])
    conn.close()
    idaccount=current_user.id
    if request.cookies.get("roleadmin") == "admin" and request.cookies.get("roleuser") != "admin" :
            
        idaccount=request.cookies.get("idaccountadminmanager")
    context={
        "request":request,
        "current_user":current_user,
        "image_path":request.cookies.get("image_path_session"),
        "roleuser":request.cookies.get("roleuser"),
        "fullname":request.cookies.get("fullname_session"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession"),
        "informationuserid":informationuserid,
        "temp":temp,
        "idaccount":idaccount,
        "readrights":request.cookies.get("readrights")
    }   
    return templates.TemplateResponse("core/healthCheckCertificates.html",context)

@core_bp.get('/educationbackground/{informationuserid}',tags=['user'], response_class=HTMLResponse)
def educationbackground_get(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    idaccount=current_user.id
    if request.cookies.get("roleadmin") == "admin" and request.cookies.get("roleuser") != "admin" :
            
        idaccount=request.cookies.get("idaccountadminmanager")
   
    conn = db.connection()
    cursor = conn.cursor()
    sql = "SELECT * from educationbackground where idinformationuser = ?"
    cursor.execute(sql,decode_id(informationuserid))
    temp = cursor.fetchall()
    df = pd.DataFrame()
    for record in temp:
        df2 = pd.DataFrame(list(record)).T
        df = pd.concat([df,df2])
    conn.close()
    context={
        "request":request,
        "current_user":current_user,
        "image_path":request.cookies.get("image_path_session"),
        "roleuser":request.cookies.get("roleuser"),
        "fullname":request.cookies.get("fullname_session"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession"),
        "informationuserid":informationuserid,
        "temp":temp,
        "idaccount":idaccount,
        "readrights":request.cookies.get("readrights")
    }
    return templates.TemplateResponse("core/educationbackground.html",context)  
@core_bp.post('/educationbackground/{informationuserid}',tags=['user'], response_class=HTMLResponse)
def educationbackground(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    idaccount=current_user.id
    if request.cookies.get("roleadmin") == "admin" and request.cookies.get("roleuser") != "admin" :
            
        idaccount=request.cookies.get("idaccountadminmanager")
   
    conn = db.connection()
    cursor = conn.cursor()
    sql = "SELECT * from educationbackground where idinformationuser = ?"
    cursor.execute(sql,decode_id(informationuserid))
    temp = cursor.fetchall()
    df = pd.DataFrame()
    for record in temp:
        df2 = pd.DataFrame(list(record)).T
        df = pd.concat([df,df2])
    conn.close()
    context={
        "request":request,
        "current_user":current_user,
        "image_path":request.cookies.get("image_path_session"),
        "roleuser":request.cookies.get("roleuser"),
        "fullname":request.cookies.get("fullname_session"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession"),
        "informationuserid":informationuserid,
        "temp":temp,
        "idaccount":idaccount,
        "readrights":request.cookies.get("readrights")
    }
    return templates.TemplateResponse("core/educationbackground.html",context) 

@core_bp.get('/qualification/{informationuserid}',tags=['user'], response_class=HTMLResponse)
def qualification_get(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    conn = db.connection()
    cursor = conn.cursor()
    sql = "SELECT * from qualification where idinformationuser = ?"
    cursor.execute(sql,decode_id(informationuserid))
    temp = cursor.fetchall()
    df = pd.DataFrame()
    for record in temp:
        df2 = pd.DataFrame(list(record)).T
        df = pd.concat([df,df2])
    conn.close()   
    idaccount=current_user.id
    if request.cookies.get("roleadmin") == "admin" and request.cookies.get("roleuser") != "admin" :
            
        idaccount=request.cookies.get("idaccountadminmanager")
    context={
        "request":request,
        "current_user":current_user,
        "image_path":request.cookies.get("image_path_session"),
        "roleuser":request.cookies.get("roleuser"),
        "fullname":request.cookies.get("fullname_session"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession"),
        "informationuserid":informationuserid,
        "temp":temp,
        "idaccount":idaccount,
        "readrights":request.cookies.get("readrights")
    }
    return templates.TemplateResponse("core/qualification.html",context)       

@core_bp.post('/qualification/{informationuserid}',tags=['user'], response_class=HTMLResponse)
def qualification(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    conn = db.connection()
    cursor = conn.cursor()
    sql = "SELECT * from qualification where idinformationuser = ?"
    cursor.execute(sql,decode_id(informationuserid))
    temp = cursor.fetchall()
    df = pd.DataFrame()
    for record in temp:
        df2 = pd.DataFrame(list(record)).T
        df = pd.concat([df,df2])
    conn.close()   
    idaccount=current_user.id
    if request.cookies.get("roleadmin") == "admin" and request.cookies.get("roleuser") != "admin" :
            
        idaccount=request.cookies.get("idaccountadminmanager")
    context={
        "request":request,
        "current_user":current_user,
        "image_path":request.cookies.get("image_path_session"),
        "roleuser":request.cookies.get("roleuser"),
        "fullname":request.cookies.get("fullname_session"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession"),
        "informationuserid":informationuserid,
        "temp":temp,
        "idaccount":idaccount,
        "readrights":request.cookies.get("readrights")
    }
    return templates.TemplateResponse("core/qualification.html",context)       
    
    
@core_bp.post('/uploadCCCD/{informationuserid}', response_class=HTMLResponse)
async def uploadCCCD(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    
    #request.cookies.get("readrights")=None
    form = CCCDForm(request)
    await form.load_data()
    informationuserid = decode_id(informationuserid)

    file_front = form.front_cccd
    file_back = form.back_cccd
    if file_front.filename == '' and file_back.filename == '':
          return RedirectResponse(f'/usercccd/{informationuserid}')
    # Check if the file has an allowed extension
    if  allowed_file(file_front.filename) or allowed_file(file_back.filename):

        found_cccd = user_cccd.find_picture_name_by_id(informationuserid)

        if file_front.filename != '':
            filename_front = secure_filename(file_front.filename)
            file_path = os.path.join(Config.UPLOAD_FOLDER, filename_front)
            print("filename: " + str(filename_front))
            # Saving the file received to the upload folder
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file_front.file, buffer)
        else:
            if found_cccd and  found_cccd[2] != '':
                
                file_front.filename = found_cccd[2]

            else:
                file_front.filename = ""
        
        if file_back.filename != '':
            filename_back = secure_filename(file_back.filename)
            file_path = os.path.join(Config.UPLOAD_FOLDER, filename_back)
            print("filename: " + str(filename_back))
            # Saving the file received to the upload folder
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file_back.file, buffer)
        else:
            if found_cccd and found_cccd[3] != '':
                file_back.filename = found_cccd[3]
                
            else:
                file_back.filename = ""

        if found_cccd:
            user_cccd.update_pic_name(informationuserid,file_front.filename,file_back.filename)
            return RedirectResponse(f'/usercccd/{informationuserid}')
            
        else:
            new_cccd = user_cccd(informationuserid = informationuserid, front_pic_name= file_front.filename,back_pic_name= file_back.filename)
            id_pic = new_cccd.save()
        
        front_cccd_session.value = file_front.filename
        back_cccd_session.value = file_back.filename
        return RedirectResponse(f'/usercccd/{informationuserid}')
      
    else:
        messages.categorary="danger"
        messages.message='Allowed media types are - png, jpg, jpeg, gif'
        context = {
           "request":request,
            "current_user":current_user,
            "form":form,
            "image_path":request.cookies.get("image_path_session"),
            "image_path_admin":request.cookies.get("image_path_session"),
            "informationuserid":encode_id(informationuserid),
            "fullname":request.cookies.get("fullname_session"),
            "roleuser":request.cookies.get("roleuser"),
            "idaccount":decode_id(current_user.id),
            "fullname_admin":request.cookies.get("fullname_adminsession"),
            "readrights":request.cookies.get("readrights"),
            "front_cccd": "",
            "back_cccd": "",
            "messages":messages.message_array(),
        }
    return templates.TemplateResponse("core/user_cccd.html",context)

@core_bp.post('/update_avatar/{informationuserid}/{idaccount}', response_class=HTMLResponse)
async def update_avatar(request:Request,informationuserid,idaccount,current_user: User = Depends(get_current_user_from_token)):
  
    #request.cookies.get("readrights")=None    
    form = AvatarForm(request)
    await form.load_data()
    informationuserid = decode_id(informationuserid)
    file = form.file
    # idaccount = decode_id(idaccount)

    
    if file.filename == '' and file.filename == '':
        return RedirectResponse(f'/userinformation/{idaccount}')
    if file and allowed_file(file.filename):
        print("file.filename: " + str(file.filename))
        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        print("filename: " + str(filename))
        # Saving the file received to the upload folder
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        id = informationuserid
        found_avatar = user_avatar.find_picture_name_by_id(id)
        if found_avatar:
            user_avatar.update_pic_name(informationuserid,file.filename)
            image_path_session.value = filename
            idaccount= (idaccount)
            return RedirectResponse(f'/userinformation/{idaccount}')
        else:
            new_avatar = user_avatar(informationuserid = id, pic_name= file.filename)
            id_pic = new_avatar.save()
            idaccount= idaccount
            return RedirectResponse(f'/userinformation/{idaccount}')
    else:
        messages.categorary="danger"
        messages.message='Allowed media types are - png, jpg, jpeg, gif'
        context = {
        "request":request,
            "current_user":current_user,
            "form":form,
            "image_path":request.cookies.get("image_path_session"),
            "image_path_admin":request.cookies.get("image_path_adminsession"),
            "informationuserid":encode_id(informationuserid),
            "fullname":request.cookies.get("fullname_session"),
            "roleuser":request.cookies.get("roleuser"),
            "idaccount":idaccount,
            "fullname_admin":request.cookies.get("fullname_adminsession"),
            "readrights":request.cookies.get("readrights"),
            "front_cccd": "",
            "back_cccd": "",
            "messages":messages.message_array(),
        }
        return templates.TemplateResponse("core/user_information.html",context)
@core_bp.get('/remove_avatar/{informationuserid}/{idaccount}', response_class=HTMLResponse)
async def remove_avatar_get(response:Response,request:Request,informationuserid,idaccount,current_user: User = Depends(get_current_user_from_token)):
   
    #request.cookies.get("readrights")=None
    response.set_cookie(key="image_path_session", value=file_path_default,httponly=True)
    #image_path_session.value = file_path_default
    user_avatar.update_pic_name(decode_id(informationuserid),file_path_default)
    return RedirectResponse(f'/userinformation/{idaccount}')

@core_bp.post('/remove_avatar/{informationuserid}/{idaccount}', response_class=HTMLResponse)
async def remove_avatar(response:Response,request:Request,informationuserid,idaccount,current_user: User = Depends(get_current_user_from_token)):
    # request.cookies.get("readrights")=None
    # image_path_session.value = file_path_default
    response.set_cookie(key="image_path_session", value=file_path_default,httponly=True)
    user_avatar.update_pic_name(decode_id(informationuserid),file_path_default)
    return RedirectResponse(f'/userinformation/{idaccount}')

@core_bp.post('/display/{filename}', response_class=HTMLResponse)
def display_image(request:Request,filename,current_user: User = Depends(get_current_user_from_token)):
    static_url = f'/static/source/{filename}'
    return RedirectResponse(url=static_url, status_code=301)

@core_bp.get('/display/{filename}', response_class=HTMLResponse)
def display_image(request:Request,filename,current_user: User = Depends(get_current_user_from_token)):
    static_url = f'/static/source/{filename}'
    return RedirectResponse(url=static_url, status_code=301)

@core_bp.post('/edit_latestEmployment/{col}/{informationuserid}', response_class=HTMLResponse)
async def edit_latestEmployment(request:Request,col,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id from informationUser where id_useraccount=?"
    cursor.execute(sql,decode_id(current_user.id))
    verify_user=cursor.fetchone()
    conn.commit()
    conn.close()
    form = EditForm(request,col)
    await form.load_data(col)
    if str(decode_id(informationuserid))==str(verify_user[0]):
        conn= db.connection()
        cursor = conn.cursor()
        sql = f"UPDATE latestEmployment SET {col} = ? WHERE idinformationuser= ?"
        new_value = getattr(form, col)
        print("job is:"+str(new_value))
        cursor.execute(sql,new_value,decode_id(informationuserid))
        cursor.commit()
        cursor.close()
        return RedirectResponse(f'/latestEmployment/{informationuserid}',status_code=status.HTTP_302_FOUND)
    elif request.cookies.get("readrights")==4:
        conn= db.connection()
        cursor = conn.cursor()
        sql = f"UPDATE latestEmployment SET {col} = ? WHERE idinformationuser= ?"
        new_value = getattr(form, col)
        cursor.execute(sql,new_value,decode_id(informationuserid))
        cursor.commit()
        cursor.close()

        idaccount= request.cookies.get("idaccountadminmanager")
        return RedirectResponse(f'/latestEmployment/{informationuserid}',status_code=status.HTTP_302_FOUND)
    
@core_bp.post('/edit_informationcccd/{col}/{informationuserid}', response_class=HTMLResponse)
async def edit_informationcccd(request:Request,col,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id from informationUser where id_useraccount=?"
    cursor.execute(sql,decode_id(current_user.id))
    verify_user=cursor.fetchone()
    conn.commit()
    conn.close()
    print("id id dddd: "+ str(informationuserid))
    informationuserid = decode_id(informationuserid)
    form = EditForm(request,col)
    await form.load_data(col)
    if str(informationuserid)==str(verify_user[0]):
        conn= db.connection()
        cursor = conn.cursor()
        sql = f"UPDATE information_cccd SET {col} = ? WHERE IdInformationUser = ?"
        
        new_value = getattr(form, col)
        print("col value: "+ col)
        print("idinformationuser: "+ str(informationuserid) )
        print("new valueeee:" + new_value)
        cursor.execute(sql,new_value,informationuserid)
        cursor.commit()
        cursor.close()
        return RedirectResponse(f'/usercccd/{encode_id(informationuserid)}',status_code=status.HTTP_302_FOUND)
    elif request.cookies.get("readrights")==4:
        conn= db.connection()
        cursor = conn.cursor()
        sql = f"UPDATE information_cccd SET {col} = ? WHERE IdInformationUser = ?"
        new_value = getattr(form, col)
        print("col value: "+ col)
        print("idinformationuser: "+ str(informationuserid) )
        print("new valueeee:" + new_value)
        cursor.execute(sql,new_value,informationuserid)
        cursor.commit()
        cursor.close()
        return RedirectResponse(f'/usercccd/{encode_id(informationuserid)}',status_code=status.HTTP_302_FOUND)
    
@core_bp.post('/upload_HCC/{informationuserid}', response_class=HTMLResponse)
async def upload_HCC(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    
    #request.cookies.get("readrights")=None
    form = HCCForm(request)
    await form.load_data()
    file = form.file
    driver = DriveAPI()
    if file.filename == '':
            return RedirectResponse(f'/healthCheckCertificates/{informationuserid}',status_code=status.HTTP_302_FOUND)
            # Check if the file has an allowed extension
    if file and allowed_attachment_file(file.filename) or file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # check if the file is image
        type = filename.split('.')[-1].lower()
        print("type is: %s" % type)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        if type not in ['docx', 'pdf']:
            
            # Saving the file received to the upload folder
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            image = Image.open(file_path)
            pdf_bytes = img2pdf.convert(image.filename)
            # document_name = file.filename.split('.')[0].lower()
            filename = f"{form.documentname}.pdf"
            pdf_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(pdf_bytes)
            image.close()
            file.close()
            print("Successfully made pdf file")
        else:
            # filename = file.filename +'.'+ filename.split('.')[-1].lower()
            # document_name = file.filename.split('.')[0].lower()
            filename = f"{form.documentname}.pdf"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        
        file_path = "static/source/" + filename
        driver.upload_file(file_path)
        # Delete the file from the server after uploading to Google Drive
        os.remove(file_path)
        _driver_file_url = driver.get_link_file_url()
        _driver_file_url=_driver_file_url.get('webContentLink')
        _attachedFileName = filename
        conn = db.connection()
        cursor = conn.cursor()
        sql = "SELECT * from healthCheckCertificates where idinformationuser = ?"
        cursor.execute(sql,decode_id(informationuserid))
        temp = cursor.fetchall()
        cursor1 = conn.cursor()
        sql="""
        DECLARE @out int;
        EXEC CountHealthCheckCertificates @IdInformationUser=?,@count = @out OUTPUT;
        SELECT @out AS the_output;
        """
        cursor1.execute(sql,decode_id(informationuserid))
        count = cursor1.fetchval()
        conn.commit()
        
        print("count is: " + str(count))
        print("HealthCheck 3")
        if count < 3 and count > 0:
            # for record in temp:
                # if record[1] == request.form.get('documentno') and record[2] != request.form.get('documentname'):
                #     flash("Documnent No and document Name are existing, please try again")
                #     return redirect(url_for('core.healthCheckCertificates',informationuserid = informationuserid, fullname = _fullname))
            # notarized_value = 1 if request.form.get('notarized') == 'Yes' else 'No'
            sql = 'INSERT INTO healthCheckCertificates (documentname, isnoratized, linkurl, idinformationuser) VALUES (?, ?, ?, ?)'
            cursor.execute(sql, filename, form.notarized, _driver_file_url, decode_id(informationuserid))
            cursor.commit() 

            conn.close()
            return RedirectResponse(f'/healthCheckCertificates/{informationuserid}',status_code=status.HTTP_302_FOUND)
        elif count ==0:
            sql = 'INSERT INTO healthCheckCertificates (documentname, isnoratized, linkurl, idinformationuser) VALUES (?, ?, ?, ?)'
            cursor.execute(sql, filename, form.notarized, _driver_file_url, decode_id(informationuserid))
            cursor.commit() 

            conn.close()
            print("HealthCheck 5")
            return RedirectResponse(f'/healthCheckCertificates/{informationuserid}',status_code=status.HTTP_302_FOUND)
        else:
            # flash("The maximum total number of documents is 3. Please try again.")
            return RedirectResponse(f'/healthCheckCertificates/{informationuserid}',status_code=status.HTTP_302_FOUND)

    else:
        # flash(' Only Allowed media types are docx,pdf, please try again!!!')
        return RedirectResponse(f'/healthCheckCertificates/{informationuserid}',status_code=status.HTTP_302_FOUND)
    
@core_bp.get('/upload_HCC/{informationuserid}', response_class=HTMLResponse)
async def upload_HCC(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    
    #request.cookies.get("readrights")=None
    form = HCCForm(request)
    await form.load_data()
    file = form.file
    driver = DriveAPI()
    if file.filename == '':
            return RedirectResponse(f'/healthCheckCertificates/{informationuserid}',status_code=status.HTTP_302_FOUND)
            # Check if the file has an allowed extension
    if file and allowed_attachment_file(file.filename) or file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # check if the file is image
        type = filename.split('.')[-1].lower()
        print("type is: %s" % type)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        if type not in ['docx', 'pdf']:
            
            # Saving the file received to the upload folder
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            image = Image.open(file_path)
            pdf_bytes = img2pdf.convert(image.filename)
            # document_name = file.filename.split('.')[0].lower()
            filename = f"{form.documentname}.pdf"
            pdf_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(pdf_bytes)
            image.close()
            file.close()
            print("Successfully made pdf file")
        else:
            # filename = file.filename +'.'+ filename.split('.')[-1].lower()
            # document_name = file.filename.split('.')[0].lower()
            filename = f"{form.documentname}.pdf"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        
        file_path = "static/source/" + filename
        driver.upload_file(file_path)
        # Delete the file from the server after uploading to Google Drive
        os.remove(file_path)
        _driver_file_url = driver.get_link_file_url()
        _driver_file_url=_driver_file_url.get('webContentLink')
        _attachedFileName = filename
        conn = db.connection()
        cursor = conn.cursor()
        sql = "SELECT * from healthCheckCertificates where idinformationuser = ?"
        cursor.execute(sql,decode_id(informationuserid))
        temp = cursor.fetchall()
        cursor1 = conn.cursor()
        sql="""
        DECLARE @out int;
        EXEC CountHealthCheckCertificates @IdInformationUser=?,@count = @out OUTPUT;
        SELECT @out AS the_output;
        """
        cursor1.execute(sql,decode_id(informationuserid))
        count = cursor1.fetchval()
        conn.commit()
        
        print("count is: " + str(count))
        print("HealthCheck 3")
        if count < 3 and count > 0:
            # for record in temp:
                # if record[1] == request.form.get('documentno') and record[2] != request.form.get('documentname'):
                #     flash("Documnent No and document Name are existing, please try again")
                #     return redirect(url_for('core.healthCheckCertificates',informationuserid = informationuserid, fullname = _fullname))
            # notarized_value = 1 if request.form.get('notarized') == 'Yes' else 'No'
            sql = 'INSERT INTO healthCheckCertificates (documentname, isnoratized, linkurl, idinformationuser) VALUES (?, ?, ?, ?)'
            cursor.execute(sql, filename, form.notarized, _driver_file_url, decode_id(informationuserid))
            cursor.commit() 

            conn.close()
            return RedirectResponse(f'/healthCheckCertificates/{informationuserid}',status_code=status.HTTP_302_FOUND)
        elif count ==0:
            sql = 'INSERT INTO healthCheckCertificates (documentname, isnoratized, linkurl, idinformationuser) VALUES (?, ?, ?, ?)'
            cursor.execute(sql, filename, form.notarized, _driver_file_url, decode_id(informationuserid))
            cursor.commit() 

            conn.close()
            print("HealthCheck 5")
            return RedirectResponse(f'/healthCheckCertificates/{informationuserid}',status_code=status.HTTP_302_FOUND)
        else:
            # flash("The maximum total number of documents is 3. Please try again.")
            return RedirectResponse(f'/healthCheckCertificates/{informationuserid}',status_code=status.HTTP_302_FOUND)

    else:
        # flash(' Only Allowed media types are docx,pdf, please try again!!!')
        return RedirectResponse(f'/healthCheckCertificates/{informationuserid}',status_code=status.HTTP_302_FOUND)
    
@core_bp.post('/upload_education/{informationuserid}', response_class=HTMLResponse)
async def upload_education(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
   
    #request.cookies.get("readrights")=None
    form = EducationForm(request)
    await form.load_data()
    file = form.file
    
    driver = DriveAPI()
    if file.filename == '':
                return RedirectResponse(f'/educationbackground/{informationuserid}',status_code=status.HTTP_302_FOUND)
            # Check if the file has an allowed extension
    if file and allowed_attachment_file(file.filename) or file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # check if the file is image
        type = filename.split('.')[-1].lower()
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        print("type is: %s" % type)
        if type not in ['docx', 'pdf']:
            # Saving the file received to the upload folder
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            image = Image.open(file_path)
            pdf_bytes = img2pdf.convert(image.filename)
            document_name = file.filename.split('.')[0].lower()
            filename = f"{document_name}.pdf"
            pdf_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            print("filename is " + filename)
            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(pdf_bytes)
            image.close()
            file.close()
            print("Successfully made pdf file")
        else:
            document_name = file.filename.split('.')[0].lower()
            filename = f"{document_name}.pdf"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        
        file_path = "static/source/" + filename
        print("filepath: " + file_path)
        driver.upload_file(file_path)
        # Delete the file from the server after uploading to Google Drive
        os.remove(file_path)
        _driver_file_url = driver.get_link_file_url()
        _driver_file_url=_driver_file_url.get('webContentLink')
        _attachedFileName = filename
        conn = db.connection()
        cursor = conn.cursor()
        sql = "SELECT * from educationbackground where idinformationuser = ?"
        print("id after decode: " + str(decode_id(informationuserid)))
        cursor.execute(sql,decode_id(informationuserid))
        temp = cursor.fetchall()
        cursor1 = conn.cursor()
        sql="""
        DECLARE @out int;
        EXEC CountEducationBackground @IdInformationUser=?,@count = @out OUTPUT;
        SELECT @out AS the_output;
        """
        
        cursor1.execute(sql,decode_id(informationuserid))
        count = cursor1.fetchval()
        print("Count is: " + str(count))
        conn.commit()
        if  count < 3:
            sql = 'INSERT INTO educationbackground VALUES (?, ?, ?, ?)'
            cursor.execute(sql, form.type, filename, _driver_file_url, decode_id(informationuserid))
            cursor.commit()
            conn.close()
            print("save successfully")
            return RedirectResponse(f'/educationbackground/{informationuserid}',status_code=status.HTTP_302_FOUND)
        else:
            # flash("The maximum total number of documents is 3. Please try again.")
           return RedirectResponse(f'/educationbackground/{informationuserid}',status_code=status.HTTP_302_FOUND)
    else:
        # flash(' Only Allowed media types are docx,pdf, please try again!!!')
       return RedirectResponse(f'/educationbackground/{informationuserid}',status_code=status.HTTP_302_FOUND)
    
@core_bp.get('/upload_education/{informationuserid}', response_class=HTMLResponse)
async def upload_education(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
   
    #request.cookies.get("readrights")=None
    form = EducationForm(request)
    await form.load_data()
    file = form.file
    
    driver = DriveAPI()
    if file.filename == '':
                return RedirectResponse(f'/educationbackground/{informationuserid}',status_code=status.HTTP_302_FOUND)
            # Check if the file has an allowed extension
    if file and allowed_attachment_file(file.filename) or file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # check if the file is image
        type = filename.split('.')[-1].lower()
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        print("type is: %s" % type)
        if type not in ['docx', 'pdf']:
            # Saving the file received to the upload folder
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            image = Image.open(file_path)
            pdf_bytes = img2pdf.convert(image.filename)
            document_name = file.filename.split('.')[0].lower()
            filename = f"{document_name}.pdf"
            pdf_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            print("filename is " + filename)
            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(pdf_bytes)
            image.close()
            file.close()
            print("Successfully made pdf file")
        else:
            document_name = file.filename.split('.')[0].lower()
            filename = f"{document_name}.pdf"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        
        file_path = "static/source/" + filename
        print("filepath: " + file_path)
        driver.upload_file(file_path)
        # Delete the file from the server after uploading to Google Drive
        os.remove(file_path)
        _driver_file_url = driver.get_link_file_url()
        _driver_file_url=_driver_file_url.get('webContentLink')
        _attachedFileName = filename
        conn = db.connection()
        cursor = conn.cursor()
        sql = "SELECT * from educationbackground where idinformationuser = ?"
        print("id after decode: " + str(decode_id(informationuserid)))
        cursor.execute(sql,decode_id(informationuserid))
        temp = cursor.fetchall()
        cursor1 = conn.cursor()
        sql="""
        DECLARE @out int;
        EXEC CountEducationBackground @IdInformationUser=?,@count = @out OUTPUT;
        SELECT @out AS the_output;
        """
        
        cursor1.execute(sql,decode_id(informationuserid))
        count = cursor1.fetchval()
        print("Count is: " + str(count))
        conn.commit()
        if  count < 3:
            sql = 'INSERT INTO educationbackground VALUES (?, ?, ?, ?)'
            cursor.execute(sql, form.type, filename, _driver_file_url, decode_id(informationuserid))
            cursor.commit()
            conn.close()
            print("save successfully")
            return RedirectResponse(f'/educationbackground/{informationuserid}',status_code=status.HTTP_302_FOUND)
        else:
            # flash("The maximum total number of documents is 3. Please try again.")
           return RedirectResponse(f'/educationbackground/{informationuserid}',status_code=status.HTTP_302_FOUND)
    else:
        # flash(' Only Allowed media types are docx,pdf, please try again!!!')
       return RedirectResponse(f'/educationbackground/{informationuserid}',status_code=status.HTTP_302_FOUND)
    
@core_bp.post('/upload_qualification/{informationuserid}', response_class=HTMLResponse)
async def upload_qualification(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
   
    #request.cookies.get("readrights")=None
    form = QualificationForm(request)
    await form.load_data()
    file = form.file
    
    driver = DriveAPI()
    if file.filename == '':
           return RedirectResponse(f'/qualification/{informationuserid}',status_code=status.HTTP_302_FOUND)
        # Check if the file has an allowed extension
    if file and allowed_attachment_file(file.filename) or file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # check if the file is image
        type = filename.split('.')[-1].lower()
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        print("type is: %s" % type)
        if type not in ['docx', 'pdf']:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            image = Image.open(file_path)
            pdf_bytes = img2pdf.convert(image.filename)
            dot_position = filename.find('.')
            document_name = file.filename.split('.')[0].lower()
            filename = f"{document_name}.pdf"
            pdf_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(pdf_bytes)
            image.close()
            file.close()
            print("Successfully made pdf file")
        else:
            document_name = file.filename.split('.')[0].lower()
            filename = f"{document_name}.pdf"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer) 
        file_path = "static/source/" + filename
        driver.upload_file(file_path)
        # Delete the file from the server after uploading to Google Drive
        os.remove(file_path)
        _driver_file_url = driver.get_link_file_url()
        _driver_file_url=_driver_file_url.get('webContentLink')
        _attachedFileName = filename
        conn = db.connection()
        cursor = conn.cursor()
        sql = "SELECT * from qualification where idinformationuser = ?"
        cursor.execute(sql,decode_id(informationuserid))
        temp = cursor.fetchall()
        cursor1 = conn.cursor()
        sql="""
        DECLARE @out int;
        EXEC CountQualification @IdInformationUser=?,@count = @out OUTPUT;
        SELECT @out AS the_output;
        """
        
        cursor1.execute(sql,decode_id(informationuserid))
        count = cursor1.fetchval()
        print("Count is: " + str(count))
        conn.commit()
        if  count < 3:
            sql = 'INSERT INTO qualification VALUES (?, ?, ?, ?)'
            cursor.execute(sql, form.type, filename, _driver_file_url, decode_id(informationuserid))
            cursor.commit()
            conn.close()
            return RedirectResponse(f'/qualification/{informationuserid}',status_code=status.HTTP_302_FOUND)
        else:
            # flash("The maximum total number of documents is 3. Please try again.")
            return RedirectResponse(f'/qualification/{informationuserid}',status_code=status.HTTP_302_FOUND)

    else:
        # flash(' Only Allowed media types are docx,pdf, please try again!!!')
       return RedirectResponse(f'/qualification/{informationuserid}',status_code=status.HTTP_302_FOUND)
    
@core_bp.get('/upload_qualification/{informationuserid}', response_class=HTMLResponse)
async def upload_qualification(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
   
    #request.cookies.get("readrights")=None
    form = EducationForm(request)
    await form.load_data()
    file = form.file
    
    driver = DriveAPI()
    if file.filename == '':
           return RedirectResponse(f'/qualification/{informationuserid}',status_code=status.HTTP_302_FOUND)
        # Check if the file has an allowed extension
    if file and allowed_attachment_file(file.filename) or file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # check if the file is image
        type = filename.split('.')[-1].lower()
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        print("type is: %s" % type)
        if type not in ['docx', 'pdf']:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            image = Image.open(file_path)
            pdf_bytes = img2pdf.convert(image.filename)
            dot_position = filename.find('.')
            document_name = file.filename.split('.')[0].lower()
            filename = f"{document_name}.pdf"
            pdf_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(pdf_bytes)
            image.close()
            file.close()
            print("Successfully made pdf file")
        else:
            document_name = file.filename.split('.')[0].lower()
            filename = f"{document_name}.pdf"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer) 
        file_path = "static/source/" + filename
        driver.upload_file(file_path)
        # Delete the file from the server after uploading to Google Drive
        os.remove(file_path)
        _driver_file_url = driver.get_link_file_url()
        _driver_file_url=_driver_file_url.get('webContentLink')
        _attachedFileName = filename
        conn = db.connection()
        cursor = conn.cursor()
        sql = "SELECT * from qualification where idinformationuser = ?"
        cursor.execute(sql,decode_id(informationuserid))
        temp = cursor.fetchall()
        cursor1 = conn.cursor()
        sql="""
        DECLARE @out int;
        EXEC CountQualification @IdInformationUser=?,@count = @out OUTPUT;
        SELECT @out AS the_output;
        """
        
        cursor1.execute(sql,decode_id(informationuserid))
        count = cursor1.fetchval()
        print("Count is: " + str(count))
        conn.commit()
        if  count < 3:
            sql = 'INSERT INTO qualification VALUES (?, ?, ?, ?)'
            cursor.execute(sql, form.type, filename, _driver_file_url, decode_id(informationuserid))
            cursor.commit()
            conn.close()
            return RedirectResponse(f'/qualification/{informationuserid}',status_code=status.HTTP_302_FOUND)
        else:
            # flash("The maximum total number of documents is 3. Please try again.")
            return RedirectResponse(f'/qualification/{informationuserid}',status_code=status.HTTP_302_FOUND)

    else:
        # flash(' Only Allowed media types are docx,pdf, please try again!!!')
       return RedirectResponse(f'/qualification/{informationuserid}',status_code=status.HTTP_302_FOUND)
    
@core_bp.get('/deleteHCC/{informationuserid}/{idhcc}',tags=['user'], response_class=HTMLResponse)
def deleteHCC_get(request:Request,informationuserid,idhcc,current_user: User = Depends(get_current_user_from_token)):
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
        sql = f"delete healthCheckCertificates WHERE id= ? and idinformationuser = ?"
        new_value = idhcc
        cursor.execute(sql,new_value,decode_id(informationuserid))
        cursor.commit()
        cursor.close()
        return RedirectResponse(f'/healthCheckCertificates/{informationuserid}',status_code=status.HTTP_302_FOUND)
        
    elif request.cookies.get("readrights")==4:
        conn= db.connection()
        cursor = conn.cursor()
        sql = f"delete healthCheckCertificates WHERE id= ? and idinformationuser = ?"
        new_value = idhcc
        cursor.execute(sql,new_value,decode_id(informationuserid))
        cursor.commit()
        cursor.close()
        return RedirectResponse(f'/healthCheckCertificates/{informationuserid}',status_code=status.HTTP_302_FOUND)
    
@core_bp.get('/deleteEducation/{informationuserid}/{ideducation}',tags=['user'], response_class=HTMLResponse)
def deleteEducation(request:Request,informationuserid,ideducation,current_user: User = Depends(get_current_user_from_token)):
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
        sql = f"delete educationbackground WHERE id= ? and idinformationuser = ?"
        new_value = ideducation
        cursor.execute(sql,new_value,decode_id(informationuserid))
        cursor.commit()
        cursor.close()
        return RedirectResponse(f'/educationbackground/{informationuserid}',status_code=status.HTTP_302_FOUND)
        
    elif request.cookies.get("readrights")==4:
        conn= db.connection()
        cursor = conn.cursor()
        sql = f"delete educationbackground WHERE id= ? and idinformationuser = ?"
        new_value = ideducation
        cursor.execute(sql,new_value,decode_id(informationuserid))
        cursor.commit()
        cursor.close()
        return RedirectResponse(f'/educationbackground/{informationuserid}',status_code=status.HTTP_302_FOUND)
    

@core_bp.get('/deleteQualification/{informationuserid}/{idqualification}',tags=['user'], response_class=HTMLResponse)
def deleteQualification(request:Request,informationuserid,idqualification,current_user: User = Depends(get_current_user_from_token)):
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
        sql = f"delete qualification WHERE id= ? and idinformationuser = ?"
        new_value = idqualification
        cursor.execute(sql,new_value,decode_id(informationuserid))
        cursor.commit()
        cursor.close()
        return RedirectResponse(f'/qualification/{informationuserid}',status_code=status.HTTP_302_FOUND)
        
    elif request.cookies.get("readrights")==4:
        conn= db.connection()
        cursor = conn.cursor()
        sql = f"delete qualification WHERE id= ? and idinformationuser = ?"
        new_value = idqualification
        cursor.execute(sql,new_value,decode_id(informationuserid))
        cursor.commit()
        cursor.close()
        return RedirectResponse(f'/qualification/{informationuserid}',status_code=status.HTTP_302_FOUND)
  