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
from globalvariable import is_admin,roleuser,rolegroup,readrights,writerights,idaccountadminmanager
from admin.forms import groupuserForm
import pyotp
from authentication.models import verifyPassword
from globalvariable import verify_password,messages,fullname_adminsession,image_path_adminsession,roleadmin
from .forms import CCCDForm,AvatarForm,HCCForm,EducationForm,QualificationForm,EditForm
from validation.forms import informationUserForm,latestEmploymentForm,usercccdForm
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
    
    #   set image path
    found_avatar = user_avatar.find_picture_name_by_id(user_temp[0])
    if found_avatar and found_avatar[2] != "":
        _image_path = found_avatar[2]
    else:
        _image_path = file_path_default
  
    _fullname = user_temp[1]

    #session['rolegroup']=""
    rolegroup.value=""
    #session['readrights']=None
    readrights.value=None
    #session['writerights']=None
    writerights.value=None

    if user_role[0]=="candidate":
        image_path = _image_path
        fullname = _fullname
        return RedirectResponse(url=f"/candidate/{image_path}/{fullname}",status_code=status.HTTP_302_FOUND)
        #return redirect(url_for("candidate.candidatepage",image_path = _image_path,fullname = _fullname))
    elif user_role[0]=="employee":
        image_path = _image_path
        fullname = _fullname
        return RedirectResponse(url=f"/employeepage/{image_path}/{fullname}",status_code=status.HTTP_302_FOUND)

    # elif user_role[0]=="employee_manager":
    #     return redirect(url_for("employeemanager.employeemanagerpage",image_path = _image_path,fullname = _fullname))
    # elif user_role[0]=="client_manager":
    #     return redirect(url_for("clientmanager.clientmanagerpage",image_path = _image_path,fullname = _fullname))
    # elif user_role[0]=="account_manager":
    #     return redirect(url_for("accountmanager.accountmanagerpage",image_path = _image_path,fullname = _fullname))
    elif user_role[0]=="admin":
        _roleadmin = "admin"
        _roleuser = ""
        _image_path_admin = file_path_default
       
        _fullname_admin = _fullname
        #session['writerights']=1
        writerights.value=1

        image_path_admin=_image_path_admin
        fullname_admin = _fullname_admin
        return RedirectResponse(url=f'/adminpage/{image_path_admin}/{fullname_admin}')
    else:
        return "You have not been granted access to the resource"

@core_bp.get("/home",tags=['user'])
def home(current_user: User = Depends(get_current_user_from_token)): 
    return authorizationUser(current_user)

@core_bp.post("/home",tags=['user'])
def home_get(current_user: User = Depends(get_current_user_from_token)): 
    return authorizationUser(current_user)

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
    return response

@core_bp.post("/logout",tags=['user'], response_class=HTMLResponse)
def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie(settings.COOKIE_NAME)
    return response

@core_bp.get("/getcodechangepassword",tags=['authentication'], response_class=HTMLResponse)
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

@core_bp.post("/getcodechangepassword",tags=['authentication'], response_class=HTMLResponse)
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
@core_bp.get('/userinformation/{idaccount}',tags=['user'], response_class=HTMLResponse)
def userinformation_get(request:Request,idaccount,current_user: User = Depends(get_current_user_from_token)):
    global _roleuser,_roleadmin,_image_path,_fullname_admin,_fullname,_image_path_admin
    #readrights.value=None    
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

        found_avatar = user_avatar.find_picture_name_by_id(user_temp[0])
        if found_avatar and found_avatar[2] != "":
            _image_path = found_avatar[2]
        else:
            _image_path = file_path_default
       
    context={
        "request":request,
        "current_user":current_user,
        "form":form,
        "image_path":_image_path,
        "informationuserid":encode_id(str(user_temp[0])),
        "fullname":user_temp[1],
        "roleuser":roleuser.value,
        "idaccount":idaccount,
        "readrights":readrights.value,
        "fullname":_fullname,
        "image_path_admin":image_path_adminsession.value,
        "roleadmin":roleadmin.value,
        "fullname_admin":fullname_adminsession.value

    }
    return templates.TemplateResponse("core/user_information.html",context)
    

@core_bp.post('/userinformation/{idaccount}',tags=['user'], response_class=HTMLResponse)
def userinformation(request:Request,idaccount,current_user: User = Depends(get_current_user_from_token)):
    global _roleuser,_roleadmin,_image_path,_fullname_admin,_fullname,_image_path_admin
    #readrights.value=None    
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

        found_avatar = user_avatar.find_picture_name_by_id(user_temp[0])
        if found_avatar and found_avatar[2] != "":
            _image_path = found_avatar[2]
        else:
            _image_path = file_path_default
    context={
        "request":request,
        "current_user":current_user,
        "form":form,
        "image_path":_image_path,
        
        "informationuserid":encode_id(str(user_temp[0])),
        "fullname":_fullname,
        "roleuser":roleuser.value,
        "idaccount":idaccount,
        "readrights":readrights.value,
        "image_path_admin":image_path_adminsession.value,
        "roleadmin":roleadmin.value,
        "fullname_admin":fullname_adminsession.value

    }
    return templates.TemplateResponse("core/user_information.html",context)
# edit information user profile
@core_bp.post('/edit_userInformation/{col}/{informationuserid}/{data_col}',tags=['user'], response_class=HTMLResponse)
async def edit_userInformation(request:Request,col,informationuserid,data_col,current_user: User = Depends(get_current_user_from_token)):
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
        
    elif readrights.value==1:
        conn= db.connection()
        cursor = conn.cursor()
        sql = f"UPDATE informationUser SET {col} = ? WHERE id= ?"
        new_value = getattr(form, col)
        cursor.execute(sql,new_value,decode_id(informationuserid))
        cursor.commit()
        cursor.close()


        
        idaccount= idaccountadminmanager.value
        return RedirectResponse(f'/userinformation/{idaccount}')
        
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
        "image_path":file_path_default,
        "roleuser":_roleuser,
        "form":form,
        "fullname":_fullname
    }
    return templates.TemplateResponse("admin/groupuserpage.html",context)

@core_bp.get('/latestEmployment/{informationuserid}',tags=['user'], response_class=HTMLResponse)
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
            print("job Title is: " + str(user_temp[2]))
            form.AnnualSalary=user_temp[3]
            form.AnnualBonus=user_temp[4]
            form.RetentionBonus=user_temp[5]
            form.RetentionBonusExpiredDate=user_temp[6]
            form.StockOption=user_temp[7]
            form.StartDate = user_temp[8]
            form.EndDate=user_temp[9]
        idaccount=current_user.id
        if roleadmin.value=="admin" :
            idaccount=idaccountadminmanager.value
        context={
        "request":request,
        "current_user":current_user,
        "image_path":file_path_default,
        "roleuser":roleuser.value,
        "form":form,
        "fullname":_fullname,
        "informationuserid":informationuserid,

       
       
        "idaccount":idaccount,
        "readrights":readrights.value,
        "image_path_admin":image_path_adminsession.value,
        "roleadmin":roleadmin.value,
        "fullname_admin":fullname_adminsession.value
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
            form.JobTitle=user_temp[2]
            print("job Title is: " + str(user_temp[2]))
            form.AnnualSalary=user_temp[3]
            form.AnnualBonus=user_temp[4]
            form.RetentionBonus=user_temp[5]
            form.RetentionBonusExpiredDate=user_temp[6]
            form.StockOption=user_temp[7]
            form.StartDate = user_temp[8]
            form.EndDate=user_temp[9]
        idaccount=current_user.id
        if roleadmin.value=="admin" :
            idaccount=idaccountadminmanager.value
        context={
        "request":request,
        "current_user":current_user,
        "image_path":file_path_default,
        "roleuser":roleuser.value,
        "form":form,
        "fullname":_fullname,
        "informationuserid":informationuserid,

       
       
        "idaccount":idaccount,
        "readrights":readrights.value,
        "image_path_admin":image_path_adminsession.value,
        "roleadmin":roleadmin.value,
        "fullname_admin":fullname_adminsession.value
        } 
        return templates.TemplateResponse("core/latestEmployment.html",context)
@core_bp.get('/usercccd/{informationuserid}',tags=['user'], response_class=HTMLResponse)
def usercccd(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    global _image_path,_front_cccd,_fullname,_roleuser
    
    # global _image_path,_front_cccd,_fullname,_roleuser
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
    if user_temp is None:
        id = 0
    else:
        id = user_temp[0]
    print("id user is %d" % id)
    found_cccd = user_cccd.find_picture_name_by_id(id)

    if found_cccd and found_cccd[2] != "":
        _front_cccd = found_cccd[2]
    else:
        _front_cccd = ""

    if found_cccd and found_cccd[3] != "":
        _back_cccd = found_cccd[3]

    else:
        _back_cccd = ""
    idaccount=current_user.id
    if roleadmin.value=="admin" :
            idaccount=idaccountadminmanager.value
    print("front image is: "+ _front_cccd) 
    print("back image is: "+ _front_cccd)
    context={
        "request":request,
        "current_user":current_user,
        "image_path":file_path_default,
        "roleuser":roleuser.value,
        "form":form,
        "fullname":_fullname,
        "informationuserid":informationuserid,
        "front_cccd":_front_cccd,
        "back_cccd":_back_cccd,
        "idaccount":idaccount,
        "readrights":readrights.value,
        "image_path_admin":image_path_adminsession.value,
        "roleadmin":roleadmin.value,
        "fullname_admin":fullname_adminsession.value
    }
    return templates.TemplateResponse("core/user_cccd.html",context)
@core_bp.post('/usercccd/{informationuserid}',tags=['user'], response_class=HTMLResponse)
def usercccd(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    global _image_path,_front_cccd,_fullname,_roleuser
    
    # global _image_path,_front_cccd,_fullname,_roleuser
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
    if user_temp is None:
        id = 0
    else:
        id = user_temp[0]
    print("id user is %d" % id)
    found_cccd = user_cccd.find_picture_name_by_id(id)

    if found_cccd and found_cccd[2] != "":
        _front_cccd = found_cccd[2]
    else:
        _front_cccd = ""

    if found_cccd and found_cccd[3] != "":
        _back_cccd = found_cccd[3]

    else:
        _back_cccd = ""
    idaccount=current_user.id
    if roleadmin.value=="admin" :
            idaccount=idaccountadminmanager.value
    print("front image is: "+ _front_cccd) 
    print("back image is: "+ _front_cccd)
    context={
        "request":request,
        "current_user":current_user,
        "image_path":file_path_default,
        "roleuser":roleuser.value,
        "form":form,
        "fullname":_fullname,
        "informationuserid":informationuserid,
        "front_cccd":_front_cccd,
        "back_cccd":_back_cccd,
        "idaccount":idaccount,
        "readrights":readrights.value,
        "image_path_admin":image_path_adminsession.value,
        "roleadmin":roleadmin.value,
        "fullname_admin":fullname_adminsession.value
    }
    return templates.TemplateResponse("core/user_cccd.html",context)
    

@core_bp.get('/healthCheckCertificates/{informationuserid}',tags=['user'],response_class=HTMLResponse)

def healthCheckCertificates(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    
    global _fullname
    
    # global _fullname
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
    if roleadmin.value=="admin" :
        idaccount=idaccountadminmanager.value
    context={
        "request":request,
        "current_user":current_user,
        "image_path":file_path_default,
        "roleuser":roleuser.value,
        "fullname":_fullname,
        "image_path_admin":image_path_adminsession.value,
        "roleadmin":roleadmin.value,
        "fullname_admin":fullname_adminsession.value,
        "informationuserid":informationuserid,
        "temp":temp,
        "idaccount":idaccount,
        "readrights":readrights.value
    }    
    return templates.TemplateResponse("core/healthCheckCertificates.html",context)
@core_bp.post('/healthCheckCertificates/{informationuserid}',tags=['user'],response_class=HTMLResponse)

def healthCheckCertificates(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    
    global _fullname
    
    # global _fullname
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
    if roleadmin.value=="admin" :
        idaccount=idaccountadminmanager.value
    context={
        "request":request,
        "current_user":current_user,
        "image_path":file_path_default,
        "roleuser":roleuser.value,
        "fullname":_fullname,
        "image_path_admin":image_path_adminsession.value,
        "roleadmin":roleadmin.value,
        "fullname_admin":fullname_adminsession.value,
        "informationuserid":informationuserid,
        "temp":temp,
        "idaccount":idaccount,
        "readrights":readrights.value
    }    
    return templates.TemplateResponse("core/healthCheckCertificates.html",context)

@core_bp.get('/educationbackground/{informationuserid}',tags=['user'], response_class=HTMLResponse)
def educationbackground(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    idaccount=current_user.id
    if roleadmin.value=="admin" :
        idaccount=idaccountadminmanager.value
    global _fullname
   
    # global _fullname
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
        "image_path":file_path_default,
        "roleuser":roleuser.value,
        "fullname":_fullname,
        "image_path_admin":image_path_adminsession.value,
        "roleadmin":roleadmin.value,
        "fullname_admin":fullname_adminsession.value,
        "informationuserid":informationuserid,
        "temp":temp,
        "idaccount":idaccount,
        "readrights":readrights.value
    }
    return templates.TemplateResponse("core/educationbackground.html",context)  
@core_bp.post('/educationbackground/{informationuserid}',tags=['user'], response_class=HTMLResponse)
def educationbackground(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    idaccount=current_user.id
    if roleadmin.value=="admin" :
        idaccount=idaccountadminmanager.value
    global _fullname
   
    # global _fullname
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
        "image_path":file_path_default,
        "roleuser":roleuser.value,
        "fullname":_fullname,
        "image_path_admin":image_path_adminsession.value,
        "roleadmin":roleadmin.value,
        "fullname_admin":fullname_adminsession.value,
        "informationuserid":informationuserid,
        "temp":temp,
        "idaccount":idaccount,
        "readrights":readrights.value
    }
    return templates.TemplateResponse("core/educationbackground.html",context)            

@core_bp.get('/qualification/{informationuserid}',tags=['user'], response_class=HTMLResponse)
def qualification(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    global _fullname
    # global _fullname
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
    if roleadmin.value=="admin" :
        idaccount=idaccountadminmanager.value 
    context={
        "request":request,
        "current_user":current_user,
        "image_path":file_path_default,
        "roleuser":roleuser.value,
        "fullname":_fullname,
        "image_path_admin":image_path_adminsession.value,
        "roleadmin":roleadmin.value,
        "fullname_admin":fullname_adminsession.value,
        "informationuserid":informationuserid,
        "temp":temp,
        "idaccount":idaccount,
        "readrights":readrights.value
    }
    return templates.TemplateResponse("core/qualification.html",context)       

@core_bp.post('/qualification/{informationuserid}',tags=['user'], response_class=HTMLResponse)
def qualification(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    global _fullname
    # global _fullname
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
    if roleadmin.value=="admin" :
        idaccount=idaccountadminmanager.value 
    context={
        "request":request,
        "current_user":current_user,
        "image_path":file_path_default,
        "roleuser":roleuser.value,
        "fullname":_fullname,
        "image_path_admin":image_path_adminsession.value,
        "roleadmin":roleadmin.value,
        "fullname_admin":fullname_adminsession.value,
        "informationuserid":informationuserid,
        "temp":temp,
        "idaccount":idaccount,
        "readrights":readrights.value
    }
    return templates.TemplateResponse("core/qualification.html",context)       
    
    
@core_bp.post('/uploadCCCD/{informationuserid}', response_class=HTMLResponse)
async def uploadCCCD(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    global _roleuser,_back_cccd,_image_path,_fullname_admin,_fullname,_image_path_admin,_roleadmin,_front_cccd
    readrights.value=None
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
        
        _front_cccd = file_front.filename
        _back_cccd = file_back.filename
        return RedirectResponse(f'/usercccd/{informationuserid}')
      
    else:
        messages.categorary="danger"
        messages.message='Allowed media types are - png, jpg, jpeg, gif'
        context = {
           "request":request,
            "current_user":current_user,
            "form":form,
            "image_path":_image_path,
            "image_path_admin":_image_path,
            "informationuserid":encode_id(informationuserid),
            "fullname":_fullname,
            "roleuser":_roleuser,
             "idaccount":decode_id(current_user.id),
            "fullname_admin":_fullname_admin,
            "readrights":readrights.value,
            "front_cccd": "",
            "back_cccd": "",
            "messages":messages.message_array(),
        }
    return templates.TemplateResponse("core/user_cccd.html",context)

@core_bp.post('/update_avatar/{informationuserid}/{idaccount}', response_class=HTMLResponse)
async def update_avatar(request:Request,informationuserid,idaccount,current_user: User = Depends(get_current_user_from_token)):
    global _roleuser,_roleadmin,_image_path,_fullname_admin,_fullname,_image_path_admin
    readrights.value=None    
    form = AvatarForm(request)
    await form.load_data()
    informationuserid = decode_id(informationuserid)
    file = form.file
    # idaccount = decode_id(idaccount)
    print("file.filename: " + str(file.filename))
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
            _image_path = filename
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
            "image_path":_image_path,
            "image_path_admin":_image_path,
            "informationuserid":encode_id(informationuserid),
            "fullname":_fullname,
            "roleuser":_roleuser,
            "idaccount":idaccount,
            "fullname_admin":_fullname_admin,
            "readrights":readrights.value,
            "front_cccd": "",
            "back_cccd": "",
            "messages":messages.message_array(),
        }
        return templates.TemplateResponse("core/user_information.html",context)
@core_bp.get('/remove_avatar/{informationuserid}', response_class=HTMLResponse)
async def remove_avatar(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    global _roleuser,_roleadmin,_image_path,_fullname_admin,_fullname,_image_path_admin
    readrights.value=None
    _image_path = file_path_default
    user_avatar.update_pic_name(decode_id(informationuserid),file_path_default)
    return RedirectResponse(f'/userinformation/{current_user.id}')

@core_bp.post('/remove_avatar/{informationuserid}', response_class=HTMLResponse)
async def remove_avatar(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    global _roleuser,_roleadmin,_image_path,_fullname_admin,_fullname,_image_path_admin
    readrights.value=None
    _image_path = file_path_default
    user_avatar.update_pic_name(decode_id(informationuserid),file_path_default)
    return RedirectResponse(f'/userinformation/{current_user.id}')

@core_bp.post('/display/{filename}', response_class=HTMLResponse)
def display_image(request:Request,filename,current_user: User = Depends(get_current_user_from_token)):
    static_url = f'/static/source/{filename}'
    return RedirectResponse(url=static_url, status_code=301)

@core_bp.get('/display/{filename}', response_class=HTMLResponse)
def display_image(request:Request,filename,current_user: User = Depends(get_current_user_from_token)):
    static_url = f'/static/source/{filename}'
    return RedirectResponse(url=static_url, status_code=301)

@core_bp.post('/edit_latestEmployment/{col}/{informationuserid}/{data_col}', response_class=HTMLResponse)
async def edit_latestEmployment(request:Request,col,informationuserid,data_col,current_user: User = Depends(get_current_user_from_token)):
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
        print("col value: "+ col)
        print("idinformationuser: "+ str(informationuserid) )
        print("new valueeee:" + new_value)
        cursor.execute(sql,new_value,decode_id(informationuserid))
        cursor.commit()
        cursor.close()
        return RedirectResponse(f'/latestEmployment/{informationuserid}')
    elif readrights.value==1:
        conn= db.connection()
        cursor = conn.cursor()
        sql = f"UPDATE latestEmployment SET {col} = ? WHERE idinformationuser= ?"
        new_value = getattr(form, col)
        cursor.execute(sql,new_value,decode_id(informationuserid))
        cursor.commit()
        cursor.close()

        idaccount= idaccountadminmanager.value
        return RedirectResponse(f'/latestEmployment/{informationuserid}')
    
@core_bp.post('/edit_informationcccd/{col}/{informationuserid}/{data_col}', response_class=HTMLResponse)
async def edit_informationcccd(request:Request,col,informationuserid,data_col,current_user: User = Depends(get_current_user_from_token)):
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
        return RedirectResponse(f'/usercccd/{encode_id(informationuserid)}')
    
@core_bp.post('/upload_HCC/{informationuserid}', response_class=HTMLResponse)
async def upload_HCC(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    global _roleuser,_back_cccd,_image_path,_fullname_admin,_fullname,_image_path_admin,_roleadmin,_front_cccd,_driver_file_url,_attachedFileName
    readrights.value=None
    form = HCCForm(request)
    await form.load_data()
    file = form.file
    driver = DriveAPI()
    if file.filename == '':
            return RedirectResponse(f'/healthCheckCertificates/{informationuserid}')
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
            return RedirectResponse(f'/healthCheckCertificates/{informationuserid}')
        elif count ==0:
            sql = 'INSERT INTO healthCheckCertificates (documentname, isnoratized, linkurl, idinformationuser) VALUES (?, ?, ?, ?)'
            cursor.execute(sql, filename, form.notarized, _driver_file_url, decode_id(informationuserid))
            cursor.commit() 

            conn.close()
            print("HealthCheck 5")
            return RedirectResponse(f'/healthCheckCertificates/{informationuserid}')
        else:
            # flash("The maximum total number of documents is 3. Please try again.")
            return RedirectResponse(f'/healthCheckCertificates/{informationuserid}')

    else:
        # flash(' Only Allowed media types are docx,pdf, please try again!!!')
        return RedirectResponse(f'/healthCheckCertificates/{informationuserid}')
    
@core_bp.get('/upload_HCC/{informationuserid}', response_class=HTMLResponse)
async def upload_HCC(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    global _roleuser,_back_cccd,_image_path,_fullname_admin,_fullname,_image_path_admin,_roleadmin,_front_cccd,_driver_file_url,_attachedFileName
    readrights.value=None
    form = HCCForm(request)
    await form.load_data()
    file = form.file
    driver = DriveAPI()
    if file.filename == '':
            return RedirectResponse(f'/healthCheckCertificates/{informationuserid}')
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
            return RedirectResponse(f'/healthCheckCertificates/{informationuserid}')
        elif count ==0:
            sql = 'INSERT INTO healthCheckCertificates (documentname, isnoratized, linkurl, idinformationuser) VALUES (?, ?, ?, ?)'
            cursor.execute(sql, filename, form.notarized, _driver_file_url, decode_id(informationuserid))
            cursor.commit() 

            conn.close()
            print("HealthCheck 5")
            return RedirectResponse(f'/healthCheckCertificates/{informationuserid}')
        else:
            # flash("The maximum total number of documents is 3. Please try again.")
            return RedirectResponse(f'/healthCheckCertificates/{informationuserid}')

    else:
        # flash(' Only Allowed media types are docx,pdf, please try again!!!')
        return RedirectResponse(f'/healthCheckCertificates/{informationuserid}')
    
@core_bp.post('/upload_education/{informationuserid}', response_class=HTMLResponse)
async def upload_education(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    global _roleuser,_back_cccd,_image_path,_fullname_admin,_fullname,_image_path_admin,_roleadmin,_front_cccd,_driver_file_url,_attachedFileName
    readrights.value=None
    form = EducationForm(request)
    await form.load_data()
    file = form.file
    
    driver = DriveAPI()
    if file.filename == '':
                return RedirectResponse(f'/educationbackground/{informationuserid}')
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
            return RedirectResponse(f'/educationbackground/{informationuserid}')
        else:
            # flash("The maximum total number of documents is 3. Please try again.")
           return RedirectResponse(f'/educationbackground/{informationuserid}')
    else:
        # flash(' Only Allowed media types are docx,pdf, please try again!!!')
       return RedirectResponse(f'/educationbackground/{informationuserid}')
    
@core_bp.get('/upload_education/{informationuserid}', response_class=HTMLResponse)
async def upload_education(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    global _roleuser,_back_cccd,_image_path,_fullname_admin,_fullname,_image_path_admin,_roleadmin,_front_cccd,_driver_file_url,_attachedFileName
    readrights.value=None
    form = EducationForm(request)
    await form.load_data()
    file = form.file
    
    driver = DriveAPI()
    if file.filename == '':
                return RedirectResponse(f'/educationbackground/{informationuserid}')
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
            return RedirectResponse(f'/educationbackground/{informationuserid}')
        else:
            # flash("The maximum total number of documents is 3. Please try again.")
           return RedirectResponse(f'/educationbackground/{informationuserid}')
    else:
        # flash(' Only Allowed media types are docx,pdf, please try again!!!')
       return RedirectResponse(f'/educationbackground/{informationuserid}')
    
@core_bp.post('/upload_qualification/{informationuserid}', response_class=HTMLResponse)
async def upload_qualification(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    global _roleuser,_back_cccd,_image_path,_fullname_admin,_fullname,_image_path_admin,_roleadmin,_front_cccd,_driver_file_url,_attachedFileName
    readrights.value=None
    form = QualificationForm(request)
    await form.load_data()
    file = form.file
    
    driver = DriveAPI()
    if file.filename == '':
           return RedirectResponse(f'/qualification/{informationuserid}')
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
            return RedirectResponse(f'/qualification/{informationuserid}')
        else:
            # flash("The maximum total number of documents is 3. Please try again.")
            return RedirectResponse(f'/qualification/{informationuserid}')

    else:
        # flash(' Only Allowed media types are docx,pdf, please try again!!!')
       return RedirectResponse(f'/qualification/{informationuserid}')
    
@core_bp.get('/upload_qualification/{informationuserid}', response_class=HTMLResponse)
async def upload_qualification(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    global _roleuser,_back_cccd,_image_path,_fullname_admin,_fullname,_image_path_admin,_roleadmin,_front_cccd,_driver_file_url,_attachedFileName
    readrights.value=None
    form = EducationForm(request)
    await form.load_data()
    file = form.file
    
    driver = DriveAPI()
    if file.filename == '':
           return RedirectResponse(f'/qualification/{informationuserid}')
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
            return RedirectResponse(f'/qualification/{informationuserid}')
        else:
            # flash("The maximum total number of documents is 3. Please try again.")
            return RedirectResponse(f'/qualification/{informationuserid}')

    else:
        # flash(' Only Allowed media types are docx,pdf, please try again!!!')
       return RedirectResponse(f'/qualification/{informationuserid}')
    