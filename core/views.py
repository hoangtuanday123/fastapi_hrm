from fastapi import APIRouter
import pandas as pd
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from authentication.models import get_current_user_from_cookie,get_current_user_from_token
from ultils import settings,encode_id,decode_id
from authentication.models import User
import db
from ultils import file_path_default
from globalvariable import is_admin,roleuser,rolegroup,readrights,writerights,idaccountadminmanager
from admin.forms import groupuserForm
import pyotp
from authentication.models import verifyPassword
from globalvariable import verify_password,messages,fullname_adminsession,image_path_adminsession,roleadmin
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

    image_path_adminsession.value=None
    fullname_adminsession.value=None
    roleadmin.value=None
    if user_role[0]=="candidate":
        image_path = file_path_default
        fullname = _fullname
        return RedirectResponse(url=f"/candidate/{image_path}/{fullname}",status_code=status.HTTP_302_FOUND)
        #return redirect(url_for("candidate.candidatepage",image_path = _image_path,fullname = _fullname))
    elif user_role[0]=="employee":
        image_path = file_path_default
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
        image_path_adminsession.value=image_path_admin
        fullname_adminsession.value=fullname_admin
        roleadmin.value="admin"
        return RedirectResponse(url=f'/adminpage/{image_path_admin}/{fullname_admin}')

       
        
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
    

@core_bp.post('/userinformation/{idaccount}', response_class=HTMLResponse)
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
        
        "informationuserid":encode_id(str(user_temp[0])),
        "fullname":user_temp[1],
        "roleuser":roleuser.value,
        "idaccount":idaccount,
        "readrights":readrights.value,
        "image_path_admin":image_path_adminsession.value,
        "roleadmin":roleadmin.value,
        "fullname_admin":fullname_adminsession.value

    }
    return templates.TemplateResponse("core/user_information.html",context)
# edit information user profile
@core_bp.post('/edit_userInformation/{col}/{informationuserid}/{data_col}', response_class=HTMLResponse)
def edit_userInformation(request:Request,col,informationuserid,data_col,current_user: User = Depends(get_current_user_from_token)):
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
        
@core_bp.get('/groupuserpage/{idinformationuser}', response_class=HTMLResponse)
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

@core_bp.get('/latestEmployment/{informationuserid}', response_class=HTMLResponse)

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
            form.Jobtittle=user_temp[2]
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

@core_bp.get('/usercccd/{informationuserid}', response_class=HTMLResponse)
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
    #found_cccd = user_cccd.find_picture_name_by_id(id)
    found_cccd=" "
    back_cccd=" "
    # if found_cccd and found_cccd[2] != "":
    #     _front_cccd = found_cccd[2]
    # else:
    #     _front_cccd = ""

    # if found_cccd and found_cccd[3] != "":
    #     _back_cccd = found_cccd[3]

    # else:
    #     _back_cccd = ""
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
    

@core_bp.get('/healthCheckCertificates/{informationuserid}',response_class=HTMLResponse)

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

@core_bp.get('/educationbackground/{informationuserid}', response_class=HTMLResponse)
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

@core_bp.get('/qualification/{informationuserid}', response_class=HTMLResponse)
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
    