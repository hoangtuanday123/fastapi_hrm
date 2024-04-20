import db
from fastapi import APIRouter,Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse,FileResponse
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from authentication.models import get_current_user_from_cookie,get_current_user_from_token
from authentication.models import User
from ultils import file_path_default,encode_id,decode_id,send_mail
from .forms import roleForm,groupuserForm
from employee.forms import Employeeinformation
from core.forms import informationUserJob,laborcontractForm,forexsalaryForm
from globalvariable import roleuser,is_admin,rolegroup,selectionItem,tablesession,messages,writerights,readrights,image_path_adminsession,fullname_adminsession,idaccountadminmanager,roleadmin
import pyotp
import pandas as pd
import pdfkit
import zipfile
from io import BytesIO
templates = Jinja2Templates(directory="templates")

admin=APIRouter()

_role_user = ""
_roleadmin = "admin"
_image_path_admin = ""
_fullname_admin = ""
@admin.get('/adminpage/{image_path_admin}/{fullname_admin}', response_class=HTMLResponse)
def adminpage_get(request: Request,image_path_admin, fullname_admin,current_user: User = Depends(get_current_user_from_token)):
    global _image_path_admin,_fullname_admin
    _image_path_admin=image_path_admin
    _fullname_admin = fullname_admin
    image_path_adminsession.value=image_path_admin
    fullname_adminsession.value=fullname_admin
    print("admin fullname is " + _fullname_admin)
    context={
        "request":request,
        "image_path_admin":_image_path_admin,
        "roleuser":_role_user,
        "roleadmin":_roleadmin,
        "fullname_admin":fullname_admin,
        "current_user":current_user
    }
    return templates.TemplateResponse("admin/adminpage.html",context)

@admin.post('/adminpage/{image_path_admin}/{fullname_admin}', response_class=HTMLResponse)
def adminpage(request: Request,image_path_admin, fullname_admin,current_user: User = Depends(get_current_user_from_token)):
    global _image_path_admin,_fullname_admin
    _image_path_admin=image_path_admin
    _fullname_admin = fullname_admin
    print("admin fullname is " + _fullname_admin)
    context={
        "request":request,
        "image_path_admin":_image_path_admin,
        "roleuser":_role_user,
        "roleadmin":_roleadmin,
        "fullname_admin":fullname_admin,
        "current_user":current_user
    }
    return templates.TemplateResponse("admin/adminpage.html",context)


@admin.get('/adminpage/roles', response_class=HTMLResponse)
async def displayRoles_get(request:Request,current_user: User = Depends(get_current_user_from_token)):
    global _image_path_admin,_fullname_admin
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from role_user"
    cursor.execute(sql)
    role_user=cursor.fetchall()
    conn.commit()
    conn.close()
    form=roleForm(request)
    role_names = [(role[0],role[1]) for role in role_user]
    context={
        "request":request,
        "data":role_names,
        "form":form,
        "image_path_admin":_image_path_admin,
        "roleadmin":_roleadmin,
        "fullname_admin":_fullname_admin,
        "roleuser":roleuser.value,
        "current_user":current_user
    }
    return templates.TemplateResponse("admin/manageRole.html",context)

@admin.post('/adminpage/roles', response_class=HTMLResponse)
async def displayRoles(request:Request,current_user: User = Depends(get_current_user_from_token)):
    global _image_path_admin,_fullname_admin
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from role_user"
    cursor.execute(sql)
    role_user=cursor.fetchall()
    conn.commit()
    conn.close()
    form=roleForm(request)
    await form.load_data()
    if await form.is_valid():
        conn=db.connection()
        cursor=conn.cursor()
        sql="insert into role_user values(?)"
        value=(form.role)
        cursor.execute(sql,value)
        conn.commit()
        conn.close()
        return RedirectResponse(url="/adminpage/roles", status_code=status.HTTP_302_FOUND)
    role_names = [(role[0],role[1]) for role in role_user]
    context={
        "request":request,
        "data":role_names,
        "form":form,
        "image_path_admin":_image_path_admin,
        "roleadmin":_roleadmin,
        "fullname_admin":_fullname_admin,
        "roleuser":roleuser.value,
        "current_user":current_user
    }
    return templates.TemplateResponse("admin/manageRole.html",context)

@admin.get("/adminpage/roles/updatepage/{idrole}", response_class=HTMLResponse)
def rolepage_get(request:Request,idrole,current_user: User = Depends(get_current_user_from_token)):
    global _image_path_admin,_fullname_admin
    conn=db.connection()
    cursor=conn.cursor()
    sql="select role_name from role_user where id=?"
    value=(idrole)
    cursor.execute(sql,value)
    rolename=cursor.fetchone()
    conn.commit()
    conn.close()
    context={
        "request":request,
        "current_user":current_user,
        "rolename":rolename[0],
        "idrole":idrole,
        "image_path_admin":_image_path_admin,
        "roleadmin":_roleadmin,
        "fullname_admin":_fullname_admin,
        "roleuser":roleuser.value
    }
    
    return templates.TemplateResponse("admin/updatepagerole.html",context)

@admin.post("/adminpage/roles/updatepage/{idrole}", response_class=HTMLResponse)
async def rolepage(request:Request,idrole,current_user: User = Depends(get_current_user_from_token)):
    global _image_path_admin,_fullname_admin
    conn=db.connection()
    cursor=conn.cursor()
    sql="select role_name from role_user where id=?"
    value=(idrole)
    cursor.execute(sql,value)
    rolename=cursor.fetchone()
    conn.commit()
    conn.close()
    if request.method=="POST":
        form = await request.form()
        new_role_name = form["user_role"]
        conn=db.connection()
        cursor=conn.cursor()
        sql="update role_user set role_name=? where id=?"
        value=(new_role_name,idrole)
        cursor.execute(sql,value)
        conn.commit()
        conn.close()
        return RedirectResponse(url="/adminpage/roles")
    context={
        "request":request,
        "current_user":current_user,
        "rolename":rolename[0],
        "idrole":idrole,
        "image_path_admin":_image_path_admin,
        "roleadmin":_roleadmin,
        "fullname_admin":_fullname_admin,
        "roleuser":roleuser.value
    }
    return templates.TemplateResponse("admin/updatepagerole.html",context)
    
@admin.post("/adminpage/roles/deleterole/{idrole}")
def deleterole(idrole):
    conn=db.connection()
    cursor=conn.cursor()
    sql="""SET NOCOUNT ON;
            EXEC deleteRole @role_id=?"""
    value=(idrole)
    cursor.execute(sql,value)
    conn.commit()
    conn.close()
    return RedirectResponse(url="/adminpage/roles")

@admin.get("/adminpage/usersmanager", response_class=HTMLResponse)
def displayusers_get(request:Request,current_user: User = Depends(get_current_user_from_token)):  
    global _image_path_admin,_fullname_admin
    totp=pyotp.TOTP('adminroles')
    totp=totp.now()
    #session['is_admin']=str(totp)
    #session['rolegroup']='admin'
    is_admin.value=str(totp)
    rolegroup.value='admin'
    _roleadmin = "admin"
    conn=db.connection()
    cursor=conn.cursor()
    sql="select u.id, i.email,r.role_name ,u.is_active,i.id from informationUser i join user_account u on i.id_useraccount=u.id join role_user r on r.id= u.role_id where u.role_id is not null"
    cursor.execute(sql)
    users=cursor.fetchall()
    conn.commit()
    conn.close()
    usersrole=[(encode_id(user[0]),user[1],user[2],user[3]) for user in users]
    #list of blocked users
    conn=db.connection()
    cursor=conn.cursor()
    sql="select u.id, i.email,r.role_name ,u.is_active,i.id from informationUser i join user_account u on i.id_useraccount=u.id join role_user r on r.id= u.role_id where u.is_active=0"
    cursor.execute(sql)
    users=cursor.fetchall()
    conn.commit()
    conn.close()
    usersblock=[(encode_id(user[0]),user[1],user[2],user[3]) for user in users]

    roles=[]
    roles.append('ALL')
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from role_user "
    cursor.execute(sql)
    roles_temp=cursor.fetchall()
    for type in roles_temp:
        roles.append(type[1])
    #roles=[role[1] for role in roles_temp]
    conn.commit()
    conn.close()
   
    table='ALL'
    #load all user 
    conn=db.connection()
    cursor=conn.cursor()
    sql="select i.*,r.role_name,i.id from informationUser i join user_account u on i.id_useraccount=u.id join role_user r on u.role_id=r.id"
    cursor.execute(sql)
    users=cursor.fetchall()
    conn.commit()
    conn.close()
    Alluser=[(user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[13]) for user in users]
     
    selecttionitem=[]
    #session['selectionItem']=selecttionitem
    selectionItem.value=selecttionitem
    context={
        "request":request,
        "current_user":current_user,
        "Alluser":Alluser,
        "usersrole":usersrole,
        "usersblock":usersblock,
        "roletype":roles,
        "table":table,
        "selecttionitem":selecttionitem,
        "image_path_admin":_image_path_admin,
        "roleadmin":_roleadmin,
        "fullname_admin":_fullname_admin,
        "roleuser":roleuser.value
    }
    return templates.TemplateResponse("admin/manageusers.html",context)
@admin.post("/adminpage/usersmanager", response_class=HTMLResponse)
async def displayusers(request:Request,current_user: User = Depends(get_current_user_from_token)):  
    #list account
    global _image_path_admin,_fullname_admin
    totp=pyotp.TOTP('adminroles')
    totp=totp.now()
    #session['is_admin']=str(totp)
    #session['rolegroup']='admin'
    is_admin.value=str(totp)
    rolegroup.value='admin'
    _roleadmin = "admin"
    conn=db.connection()
    cursor=conn.cursor()
    sql="select u.id, i.email,r.role_name ,u.is_active,i.id from informationUser i join user_account u on i.id_useraccount=u.id join role_user r on r.id= u.role_id where u.role_id is not null"
    cursor.execute(sql)
    users=cursor.fetchall()
    conn.commit()
    conn.close()
    usersrole=[(encode_id(user[0]),user[1],user[2],user[3]) for user in users]
    #list of blocked users
    conn=db.connection()
    cursor=conn.cursor()
    sql="select u.id, i.email,r.role_name ,u.is_active,i.id from informationUser i join user_account u on i.id_useraccount=u.id join role_user r on r.id= u.role_id where u.is_active=0"
    cursor.execute(sql)
    users=cursor.fetchall()
    conn.commit()
    conn.close()
    usersblock=[(encode_id(user[0]),user[1],user[2],user[3]) for user in users]

    roles=[]
    roles.append('ALL')
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from role_user "
    cursor.execute(sql)
    roles_temp=cursor.fetchall()
    for type in roles_temp:
        roles.append(type[1])
    #roles=[role[1] for role in roles_temp]
    conn.commit()
    conn.close()
   
    table='ALL'
    #load all user 
    conn=db.connection()
    cursor=conn.cursor()
    sql="select i.*,r.role_name,i.id from informationUser i join user_account u on i.id_useraccount=u.id join role_user r on u.role_id=r.id"
    cursor.execute(sql)
    users=cursor.fetchall()
    conn.commit()
    conn.close()
    Alluser=[(user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[13]) for user in users]
     
    selecttionitem=[]
    #session['selectionItem']=selecttionitem
    selectionItem.value=selecttionitem
    form = await request.form()
    
    if request.method=='POST' and 'fillter' in form and form["fillter"]=='fillter':
        table=form['roletype']
        if table=='candidate':
            #session['table']='candidate'
            tablesession.value='candidate'
            roles.remove('candidate')
            roles.insert(0, 'candidate')
            conn=db.connection()
            cursor=conn.cursor()
            sql="select i.*,r.role_name from informationUser i  join user_account u on i.id_useraccount=u.id join role_user r on u.role_id=r.id where r.role_name='candidate'"
            cursor.execute(sql)
            users=cursor.fetchall()
            conn.commit()
            conn.close()
            Alluser=[(user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[13]) for user in users]
        elif table=='ALL':
            #session['table']='ALL'
            tablesession.value='ALL'
            roles.remove('ALL')
            roles.insert(0, 'ALL')
            conn=db.connection()
            cursor=conn.cursor()
            sql="select i.*,r.role_name from informationUser i join user_account u on i.id_useraccount=u.id join role_user r on u.role_id=r.id"
            cursor.execute(sql)
            users=cursor.fetchall()
            conn.commit()
            conn.close()
            Alluser=[(user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[13]) for user in users]
        elif table=='employee':
            #session['table']='employee'
            tablesession.value='employee'
            roles.remove('employee')
            roles.insert(0, 'employee')
            conn=db.connection()
            cursor=conn.cursor()
            sql="select i.*,r.role_name from informationUser i  join user_account u on i.id_useraccount=u.id join role_user r on u.role_id=r.id where r.role_name='employee'"
            cursor.execute(sql)
            users=cursor.fetchall()
            conn.commit()
            conn.close()
            Alluser=[(user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[13]) for user in users]
    elif 'exportexcel' in form and form['exportexcel']=='exportexcel':
        selecttionitem=form.getlist('checkbox')
        selectionItem.value=selecttionitem
        #table=session.get('table')
        table=tablesession.value
        if(table==None or table=='ALL'):
            table='ALL'
            typerole=table
            return RedirectResponse(url=f"/adminpage/usersmanager/exportfileexcel/{typerole}")
        else:
            typerole=table
            return RedirectResponse(url=f"/adminpage/usersmanager/exportfileexcel/{typerole}")
        # check1=is_all_null(selecttionitem)
        # if check1==False:
        #     #return str(table)
        #     typerole=table
        #     return RedirectResponse(url=f"/adminpage/usersmanager/exportfileexcel/{typerole}")
        # else:
        #     #session['selectionItem']=[]
        #     selectionItem.value=[]
        #     typerole=table
        #     return RedirectResponse(url=f"/adminpage/usersmanager/exportfileexcel/{typerole}")
    elif form['exportpdf']=='exportpdf':
        selecttionitem=form.getlist('checkbox')
        selectionItem.value=selecttionitem
        Selecttionitem=[]
        if selectionItem.value:
            Selecttionitem=selectionItem.value
        #table=session.get('table')
        table=tablesession.value
        
        if(table==None):
            table='ALL'
        check= is_all_null(Selecttionitem)
        if check==False:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                for id in Selecttionitem:
                    if(str(id)!='None'):
                        pdf_content = exportfilepdf(request,str(id),table)
            
                        zip_file.writestr(f'output'+id+'.pdf', pdf_content)
            zip_buffer.seek(0)
            response = Response(zip_buffer.read())
            response.headers["Content-Disposition"] = "attachment; filename=your_zip_file_pdf.zip"
            response.headers["Content-Type"] = "application/zip"

            return response
        else:
            Selecttionitem=[]
            for user in Alluser:
                if user[12]==table :
                   Selecttionitem.append(str(user[0]))
                if table=='ALL':
                    Selecttionitem.append(str(user[0]))
            #session['selectionItem']=Selecttionitem
            selectionItem.value=Selecttionitem
            #Selecttionitem=session.get('selectionItem', [])
            Selecttionitem=[]
            if selectionItem.value:
                Selecttionitem=selectionItem.value
            #return Selecttionitem
            #return table
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                for id in Selecttionitem:
                    if(str(id)!='None'):
                        
                        pdf_content = exportfilepdf(request,str(id),table)
            
                        zip_file.writestr(f'output'+id+'.pdf', pdf_content)
            zip_buffer.seek(0)
            response = Response(zip_buffer.read())
            response.headers["Content-Disposition"] = "attachment; filename=your_zip_file_pdf.zip"
            response.headers["Content-Type"] = "application/zip"

            return response
        #return redirect(url_for("admin.exportfilepdf"))

    context={
        "request":request,
        "current_user":current_user,
        "Alluser":Alluser,
        "usersrole":usersrole,
        "usersblock":usersblock,
        "roletype":roles,
        "table":table,
        "selecttionitem":selecttionitem,
        "image_path_admin":_image_path_admin,
        "roleadmin":_roleadmin,
        "fullname_admin":_fullname_admin,
        "roleuser":roleuser.value
    }
    return templates.TemplateResponse("admin/manageusers.html",context)
    # return render_template("admin/manageusers.html",Alluser=Alluser,usersrole=usersrole,usersblock=usersblock,
    #                        roletype=roles,table=table,selecttionitem=selecttionitem,image_path_admin=_image_path_admin,roleadmin=_roleadmin,fullname_admin =  _fullname_admin
    #                        ,totp=totp,roleuser=session.get('roleuser'))

def is_all_null(array):
    for e in array:
        if e is not None:
            return False  # Nếu có ít nhất một phần tử không phải None, trả về False
    return True  # Nếu tất cả các phần tử đều là None, trả về True

@admin.post('/adminpage/usersmanager/exportfileexcel/{typerole}', response_class=HTMLResponse)
def exportfileexcel(typerole,current_user: User = Depends(get_current_user_from_token)):
    #Selecttionitem=session.get('selectionItem', [])
    Selecttionitem=[]
    if selectionItem.value:
        Selecttionitem=selectionItem.value
    if typerole=='ALL':
        usersrole=[]
         
        if Selecttionitem !=[]:
            
            for id in Selecttionitem:
                if(str(id)!='None'):
                    
                    conn=db.connection()
                    cursor=conn.cursor()
                    sql="select i.*,l.* from informationUser i join latestEmployment l on l.idinformationuser=i.id join user_account u on i.id_useraccount=u.id where i.id=?"
                    cursor.execute(sql,str(id))
                    user=cursor.fetchone()
                    conn.commit()
                    conn.close()
                    usersrole.append((user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[14],user[15],user[16],user[17],user[18],user[19],user[20],user[21],user[22]))
        else:
            
            conn=db.connection()
            cursor=conn.cursor()
            sql="select i.*,l.* from informationUser i join latestEmployment l on l.idinformationuser=i.id join user_account u on i.id_useraccount=u.id"
            cursor.execute(sql)
            users1=cursor.fetchall()
            conn.commit()
            conn.close()
            usersrole=[(user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[14],user[15],user[16],user[17],user[18],user[19],user[20],user[21],user[22]) for user in users1]
        df = pd.DataFrame(usersrole, columns=['id', 'fullname', 'nickname', 'email','contactaddress','phone','linkedln','years','location','maritalstatus','ethnicgroup','religion','employer','jobtitle','annual salary','annual bonus','retention bonus'
                                              ,'retention bonus expired date','stock option','start date','end date'])
        file_path='information_All_Account_User.xlsx'
        df.to_excel(file_path, sheet_name='Sheet_name_1')
        # response=send_from_directory('.',file_path,as_attachment=True)
        # response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        # response.headers["Pragma"] = "no-cache"
        # response.headers["Expires"] = "0"
        # flash("export file successfully")
        #return response
        return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
    elif typerole=='candidate':
        usersrole=[]
        if Selecttionitem !=[]:
            for id in Selecttionitem:
                if(str(id)!='None'):
                    
                    conn=db.connection()
                    cursor=conn.cursor()
                    sql="select i.*,l.* from informationUser i join latestEmployment l on l.idinformationuser=i.id join user_account u on i.id_useraccount=u.id join role_user r on u.role_id=r.id where r.role_name='candidate' and i.id=?"
                    cursor.execute(sql,str(id))
                    user=cursor.fetchone()
                    conn.commit()
                    conn.close()
                    usersrole.append((user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[14],user[15],user[16],user[17],user[18],user[19],user[20],user[21],user[22]) )
            
        else:
            conn=db.connection()
            cursor=conn.cursor()
            sql="select i.*,l.* from informationUser i join latestEmployment l on l.idinformationuser=i.id join user_account u on i.id_useraccount=u.id join role_user r on u.role_id=r.id where r.role_name='candidate'"
            cursor.execute(sql)
            users2=cursor.fetchall()
            conn.commit()
            conn.close()
            usersrole=[(user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[14],user[15],user[16],user[17],user[18],user[19],user[20],user[21],user[22]) for user in users2]
        df = pd.DataFrame(usersrole, columns=['id', 'fullname', 'nickname', 'email','contactaddress','phone','linkedln','years','location','maritalstatus','ethnicgroup','religion','employer','jobtitle','annual salary','annual bonus','retention bonus'
                                              ,'retention bonus expired date','stock option','start date','end date'])
        file_path='information_candidates.xlsx'
        df.to_excel(file_path, sheet_name='Sheet_name_1')
        # response=send_from_directory('.',file_path,as_attachment=True)
        # response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        # response.headers["Pragma"] = "no-cache"
        # response.headers["Expires"] = "0"
        # flash("export file successfully")
        # return response
        return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    elif typerole=='employee':
        usersrole=[]
        
        if Selecttionitem !=[]:
            for id in Selecttionitem:
                if(str(id)!='None'):
                    
                    conn=db.connection()
                    cursor=conn.cursor()
                    sql="""select i.*,ij.*,l.*,f.*,ft.type,r.role_name from  informationUser i join informationUserJob ij on i.id=ij.idinformationuser join laborContract l on
                        ij.id=l.idinformationUserJob join forexSalary f on ij.id=f.idinformationUserJob join forextype ft on ft.id=f.forextypeid join user_account u on i.id_useraccount=u.id
                        join role_user r on u.role_id=r.id where r.role_name='employee' and ij.is_active=1 and l.is_active=1 and f.is_active=1 and i.id=?"""
                    cursor.execute(sql,str(id))
                    user=cursor.fetchone()
                    conn.commit()
                    conn.close()
                    usersrole.append((user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[14],user[15],user[16],user[17],
                        user[18],user[19],user[20],user[21],user[22],user[23],user[24],user[28],user[29],user[30],user[31],user[32],user[33],user[45],user[38],user[39],
                        user[40],user[41],user[42],user[46]))
            
        else:
            conn=db.connection()
            cursor=conn.cursor()
            sql="""select i.*,ij.*,l.*,f.*,ft.type,r.role_name from  informationUser i join informationUserJob ij on i.id=ij.idinformationuser join laborContract l on
                ij.id=l.idinformationUserJob join forexSalary f on i.id=f.idinformationUserJob join forextype ft on ft.id=f.forextypeid join user_account u on i.id_useraccount=u.id
                join role_user r on u.role_id=r.id where r.role_name='employee' and ij.is_active=1 and l.is_active=1 and f.is_active=1"""
            cursor.execute(sql)
            users3=cursor.fetchall()
            conn.commit()
            conn.close()
            usersrole=[(user[0],user[1],user[2],user[3],user[4],user[6],user[7],user[8],user[9],user[10],user[11],user[12],user[14],user[15],user[16],user[17],
                        user[18],user[19],user[20],user[21],user[22],user[23],user[24],user[28],user[29],user[30],user[31],user[32],user[33],user[45],user[38],user[39],
                        user[40],user[41],user[42],user[46]) for user in users3]
        df = pd.DataFrame(usersrole, columns=['id', 'fullname', 'nickname', 'email','contactaddress','phone','linkedln','years','location','maritalstatus','ethnicgroup','religion','companysite','department',
                                              'directmanager','workfortype','bankaccount','bankname','taxcode','Socialinsurancecode','Healthinsurancecardcode','Registeredhospitalcode','Registeredhospitalname',
                                              'LaborcontractNo','Laborcontracttype','Laborcontractterm','Commencementdate','Position','Employeelevel','type','Annualsalary','Annualbonustarget','Monthlysalary','Monthlysalaryincontract',
                                              'Quaterlybonustarget','role_name'])
            
        file_path='information_employee.xlsx'
        df.to_excel(file_path, sheet_name='Sheet_name_1')
        # response=send_from_directory('.',file_path,as_attachment=True)
        # response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        # response.headers["Pragma"] = "no-cache"
        # response.headers["Expires"] = "0"
        # flash("export file successfully")
        # return response
        return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

def exportfilepdf(request:Request,idinformationuser,type):
    _roleuser=""
    if type=='candidate':
    
    #form = informationUserForm()
        conn=db.connection()
        cursor=conn.cursor()
        sql="""select i.*,l.*,r.role_name from informationUser i join latestEmployment l on 
        i.id=l.idinformationuser join user_account u on u.id=i.id_useraccount 
        join role_user r on r.id=u.role_id and r.role_name='candidate'  where i.id=?
        """
        value=(idinformationuser)
        cursor.execute(sql,value)
        user_temp=cursor.fetchone()
        conn.commit()
        conn.close()
        user=[user_temp[0],user_temp[1], user_temp[2], user_temp[3], user_temp[4],user_temp[5], user_temp[6], user_temp[7],
                                    user_temp[8], user_temp[9], user_temp[10], user_temp[11], user_temp[12],user_temp[13],user_temp[14],
                                    user_temp[15],user_temp[16],user_temp[17],user_temp[18],user_temp[19],user_temp[20],user_temp[21],user_temp[22],user_temp[24]]
        context={
            "request":request,
            "image_path":file_path_default,
            "informationuserid":user_temp[0],
            "user":user,
            "roleuser":_roleuser
        }
        html=templates.TemplateResponse("admin/exportpdfinformationuser.html",context).body.decode("utf-8")
        # html= render_template("admin/exportpdfinformationuser.html", image_path = file_path_default,informationuserid =  user_temp[0],
        #                     user=user, roleuser= _roleuser )
        pdf=pdfkit.from_string(str(html),False,options={"enable-local-file-access": ""})
        return pdf  
    elif type=='employee':

    #form = informationUserForm()
        conn=db.connection()
        cursor=conn.cursor()
        sql="""select i.*,l.*,r.role_name from informationUser i join latestEmployment l on 
        i.id=l.idinformationuser join user_account u on u.id=i.id_useraccount 
        join role_user r on r.id=u.role_id and r.role_name='employee'  where i.id=?
        """
        value=(idinformationuser)
        cursor.execute(sql,value)
        user_temp=cursor.fetchone()
        conn.commit()
        conn.close()
        user=[user_temp[0],user_temp[1], user_temp[2], user_temp[3], user_temp[4],user_temp[5], user_temp[6], user_temp[7],
                                    user_temp[8], user_temp[9], user_temp[10], user_temp[11], user_temp[12],user_temp[13],user_temp[14],
                                    user_temp[15],user_temp[16],user_temp[17],user_temp[18],user_temp[19],user_temp[20],user_temp[21],user_temp[22],user_temp[24]]
        context={
            "request":request,
            "image_path":file_path_default,
            "informationuserid":user_temp[0],
            "user":user,
            "roleuser":_roleuser
        }
        html=templates.TemplateResponse("admin/exportpdfinformationuser.html",context).body.decode("utf-8")
        # html= render_template("admin/exportpdfinformationuser.html", image_path = file_path_default,informationuserid =  user_temp[0],
        #                     user=user, roleuser= _roleuser )
        pdf=pdfkit.from_string(str(html),False,options={"enable-local-file-access": ""})
        return pdf  
    elif type=='ALL':

    #form = informationUserForm()
        conn=db.connection()
        cursor=conn.cursor()
        sql="""select i.*,l.*,r.role_name from informationUser i join latestEmployment l on 
        i.id=l.idinformationuser join user_account u on u.id=i.id_useraccount 
        join role_user r on r.id=u.role_id   where i.id=?
        """
        value=(idinformationuser)
        cursor.execute(sql,value)
        user_temp=cursor.fetchone()
        conn.commit()
        conn.close()
        user=[user_temp[0],user_temp[1], user_temp[2], user_temp[3], user_temp[4],user_temp[5], user_temp[6], user_temp[7],
                                    user_temp[8], user_temp[9], user_temp[10], user_temp[11], user_temp[12],user_temp[13],user_temp[14],
                                    user_temp[15],user_temp[16],user_temp[17],user_temp[18],user_temp[19],user_temp[20],user_temp[21],user_temp[22],user_temp[24]]
        context={
            "request":request,
            "image_path":file_path_default,
            "informationuserid":user_temp[0],
            "user":user,
            "roleuser":_roleuser
        }
        html=templates.TemplateResponse("admin/exportpdfinformationuser.html",context).body.decode("utf-8")
        # html= render_template("admin/exportpdfinformationuser.html", image_path = file_path_default,informationuserid =  user_temp[0],
        #                     user=user, roleuser= _roleuser )
        pdf=pdfkit.from_string(str(html),False,options={"enable-local-file-access": ""})
        return pdf  
    
@admin.get("/adminpage/usersmanager/assignrole/{idaccount}/{userrole}", response_class=HTMLResponse)
def assignrole_get(request:Request,idaccount,userrole,current_user: User = Depends(get_current_user_from_token)):
    global _image_path_admin,_fullname_admin
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id from informationUser where id_useraccount=?"
    value=(decode_id(idaccount))
    cursor.execute(sql,value)
    idinformation_temp=cursor.fetchone()
    conn.commit()
    conn.close()
    idinformationuser=idinformation_temp[0]

    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from role_user"
    cursor.execute(sql)
    roles_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    roles=[(role[1]) for role in roles_temp]

    conn=db.connection()
    cursor=conn.cursor()
    sql="select  i.email from informationUser i join user_account u on i.id_useraccount=u.id where u.id=?"
    value=decode_id(idaccount)
    cursor.execute(sql,value)
    email=cursor.fetchall()
    conn.commit()
    conn.close()
    a=None
    b=None
    context={
        "request":request,
        "current_user":current_user,
        "roles":roles,
        "email":email[0],
        "idaccount":idaccount,
        "roleuser":roleuser.value,
        "userrole":userrole,
        "informationuserid":encode_id(idinformationuser),
        "image_path_admin":_image_path_admin,
        "roleadmin":_roleadmin,
        "fullname_admin":_fullname_admin
    }
    return templates.TemplateResponse("admin/updatepageuserrole.html",context)

@admin.post("/adminpage/usersmanager/assignrole/{idaccount}/{userrole}", response_class=HTMLResponse)
async def assignrole(request:Request,idaccount,userrole,current_user: User = Depends(get_current_user_from_token)):
    global _image_path_admin,_fullname_admin
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id from informationUser where id_useraccount=?"
    value=(decode_id(idaccount))
    cursor.execute(sql,value)
    idinformation_temp=cursor.fetchone()
    conn.commit()
    conn.close()
    idinformationuser=idinformation_temp[0]

    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from role_user"
    cursor.execute(sql)
    roles_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    roles=[(role[1]) for role in roles_temp]

    conn=db.connection()
    cursor=conn.cursor()
    sql="select  i.email from informationUser i join user_account u on i.id_useraccount=u.id where u.id=?"
    value=decode_id(idaccount)
    cursor.execute(sql,value)
    email=cursor.fetchall()
    conn.commit()
    conn.close()
    a=None
    b=None

    if request.method=="POST":
        form = await request.form()
        for role in roles_temp:
            if form["roles"]==role[1] or form["roles"]==None:
                a=role[0]
                b=role[1]
                break
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from informationUserJob ij join informationUser i on ij.idinformationuser=i.id where id_useraccount=?"
        values=(decode_id(idaccount))
        cursor.execute(sql,values)
        validate=cursor.fetchone()
        conn.commit()
        conn.close()
        if(b=='employee'and validate == None):
            messages.value=[('info','please enter information job employee before assign role employee')]
            return RedirectResponse(url="/adminpage/usersmanager", status_code=status.HTTP_302_FOUND)
        else:
            conn=db.connection()
            cursor=conn.cursor()
            sql="update user_account set role_id=? where id=?"
            values=(a,idaccount)
            cursor.execute(sql,values)
            conn.commit()
            conn.close()
            return RedirectResponse(url="/adminpage/usersmanager", status_code=status.HTTP_302_FOUND)
    #return userrole
    context={
        "request":request,
        "current_user":current_user,
        "roles":roles,
        "email":email[0],
        "idaccount":idaccount,
        "roleuser":roleuser.value,
        "userrole":userrole,
        "informationuserid":encode_id(idinformationuser),
        "image_path_admin":_image_path_admin,
        "roleadmin":_roleadmin,
        "fullname_admin":_fullname_admin
    }
    return templates.TemplateResponse("admin/updatepageuserrole.html",context)

@admin.get('/adminpage/usersmanager/blockuser/{idaccount}')
def blockaccount(idaccount,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="update user_account set is_active=0 where id=?"
    values=(decode_id(idaccount))
    cursor.execute(sql,values)
    conn.commit()
    conn.close()
    messages=('success','block account '+idaccount+' successfully')
    return RedirectResponse(url="/adminpage/usersmanager", status_code=status.HTTP_302_FOUND)

@admin.get('/adminpage/usersmanager/openblock/{idaccount}')
def openblock(idaccount,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="update user_account set is_active=1 where id=?"
    values=(decode_id(idaccount))
    cursor.execute(sql,values)
    conn.commit()
    conn.close()
    messages=('open account '+ str(decode_id(idaccount)) + ' successfully')
    return RedirectResponse(url="/adminpage/usersmanager", status_code=status.HTTP_302_FOUND) 

@admin.get('/adminpage/usersmanager/lookinformationuser/{idaccount}')
def info(idaccount,current_user: User = Depends(get_current_user_from_token)):
    idaccount_encode=idaccount
    idaccountadminmanager.value=idaccount
    conn=db.connection()
    cursor=conn.cursor()
    sql="select r.role_name from user_account u join role_user r on u.role_id=r.id where u.id=?"
    value=(decode_id(idaccount_encode))
    cursor.execute(sql,value)
    user_role=cursor.fetchone()
    #session['roleuser']=user_role[0]
    roleuser.value=user_role[0]
    roleadmin.value="admin"
    return RedirectResponse(url=f"/userinformation/{idaccount_encode}", status_code=status.HTTP_302_FOUND)

def readrights_func(rolegroup):
    if rolegroup=="manager" or rolegroup=="admin":
        readrights.value=4
        writerights.value=1
        #session["readrights"]=4
        # session['writerights']=1
    elif rolegroup=="leader":
        readrights.value=3
        #["readrights"]=3
    elif rolegroup=="member" or rolegroup=="client":
        readrights.value=2
        #session["readrights"]=2
    else:
        readrights.value=5
        #session["readrights"]=5

@admin.get('/adminpage/groupuserpage', response_class=HTMLResponse)
async def groupuserpage_get(request:Request,current_user: User = Depends(get_current_user_from_token)):
    _roleadmin = "admin"
    rolegroup.value='admin'
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from groupuser"
    cursor.execute(sql)
    grouptemp=cursor.fetchall()
    conn.commit()
    conn.close()
    groups=[(group[0],group[1],group[2],'admin') for group in grouptemp]
    form =groupuserForm(request)
    context={
        "request":request,
        "current_user":current_user,
        "groups":groups,
        "image_path":file_path_default,
        "roleuser":roleuser.value,
        "form":form,
        "rolegroup":'admin',
        "roleadmin":_roleadmin,
        "image_path_admin":_image_path_admin,
        "fullname_admin":_fullname_admin
    }
    return templates.TemplateResponse("admin/groupuserpage.html",context)
@admin.post('/adminpage/groupuserpage', response_class=HTMLResponse)
async def groupuserpage(request:Request,current_user: User = Depends(get_current_user_from_token)):
    _roleadmin = "admin"
    rolegroup.value='admin'
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from groupuser"
    cursor.execute(sql)
    grouptemp=cursor.fetchall()
    conn.commit()
    conn.close()
    groups=[(group[0],group[1],group[2],'admin') for group in grouptemp]
    form =groupuserForm(request)
    await form.load_data()
    if  form.is_valid():
        conn=db.connection()
        cursor=conn.cursor()
        sql="""SET NOCOUNT ON;
                DECLARE @id int;
                insert into groupuser(name,createddate) values(?,GETDATE())
                SET @id = SCOPE_IDENTITY();            
                SELECT @id AS the_output;"""
        value=(form.group)
        cursor.execute(sql,value)
        idgrouptemp=cursor.fetchone()
        conn.commit()
        conn.close()
        idgroup=idgrouptemp[0]
        rolegroupvalue='admin'
        return RedirectResponse(url=f"/adminpage/groupuserpage/updategroupuser/{idgroup}/{rolegroupvalue}", status_code=status.HTTP_302_FOUND)
    context={
        "request":request,
        "current_user":current_user,
        "groups":groups,
        "image_path":file_path_default,
        "roleuser":roleuser.value,
        "form":form,
        "rolegroup":'admin',
        "roleadmin":_roleadmin,
        "image_path_admin":_image_path_admin,
        "fullname_admin":_fullname_admin
    }
    return templates.TemplateResponse("admin/groupuserpage.html",context)

@admin.get('/adminpage/groupuserpage/updategroupuser/{idgroup}/{rolegroupvalue}',response_class=HTMLResponse)
async def updategropuser_get(request:Request,idgroup,rolegroupvalue,current_user: User = Depends(get_current_user_from_token)):
    readrights_func(rolegroupvalue)
    rolegroup.value=rolegroupvalue
    
    if str(rolegroup.value) !='admin':
        _roleadmin=""
    else:
        _roleadmin = "admin"
    form =groupuserForm(request)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from groupuser where id=?"
    value=(idgroup)
    cursor.execute(sql,value)
    group=cursor.fetchone()
    conn.commit()
    conn.close()

    usersSelect=[]
    usersSelect.append((0,' '))
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id,email from informationUser"
    cursor.execute(sql)
    usersSelecttemp=cursor.fetchall()
    conn.commit()
    conn.close()
    for user in usersSelecttemp:
        usersSelect.append((user[0],user[1]))


    grouprole=[]
    grouprole.append((0,' '))
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from rolegroupuser"
    cursor.execute(sql)
    grouproletemp=cursor.fetchall()
    conn.commit()
    conn.close()
    for role in grouproletemp:
        grouprole.append((role[0],role[1]))

    conn=db.connection()
    cursor=conn.cursor()
    sql="""select gd.id, i.Fullname,r.rolename,g.name,gd.createddate,u.id from groupuserdetail gd join informationUser i on i.id=gd.iduser join rolegroupuser r on gd.idrolegroupuser=r.id
            join groupuser g on gd.idgroupuser=g.id join user_account u on u.id=i.id_useraccount where g.id=?"""
    value=(idgroup)
    cursor.execute(sql,value)
    userstemp=cursor.fetchall()
    conn.commit()
    conn.close()
    users=[(user[0],user[1],user[2],user[3],user[4],encode_id(user[5])) for user in userstemp]
    form.group=group[1]
    form.alias=group[4]
    form.email=group[5]
    form.url=group[6]
    form.description=group[7]
    context={
        "request":request,
        "current_user":current_user,
        "idgroup":idgroup,
        "image_path":file_path_default,
        "roleuser":roleuser.value,
        "usersSelect":usersSelect,
        "grouprole":grouprole,
        "users":users,
        "rolegroup":rolegroupvalue,
        #totp=str(totp),
        "form":form,
        "roleadmin" : _roleadmin,
        "image_path_admin":_image_path_admin,
        "fullname_admin" : _fullname_admin
    }
    return templates.TemplateResponse("admin/updategroupuser.html",context)

@admin.post('/adminpage/groupuserpage/updategroupuser/{idgroup}/{rolegroupvalue}',response_class=HTMLResponse)
async def updategropuser(request:Request,idgroup,rolegroupvalue,current_user: User = Depends(get_current_user_from_token)):
    readrights_func(rolegroupvalue)
    rolegroup.value=rolegroupvalue
    if str(rolegroup.value) !='admin':
        _roleadmin=""
    else:
        _roleadmin = "admin"
    form =groupuserForm(request)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from groupuser where id=?"
    value=(idgroup)
    cursor.execute(sql,value)
    group=cursor.fetchone()
    conn.commit()
    conn.close()

    usersSelect=[]
    usersSelect.append((0,' '))
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id,email from informationUser"
    cursor.execute(sql)
    usersSelecttemp=cursor.fetchall()
    conn.commit()
    conn.close()
    for user in usersSelecttemp:
        usersSelect.append((user[0],user[1]))


    grouprole=[]
    grouprole.append((0,' '))
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from rolegroupuser"
    cursor.execute(sql)
    grouproletemp=cursor.fetchall()
    conn.commit()
    conn.close()
    for role in grouproletemp:
        grouprole.append((role[0],role[1]))

    conn=db.connection()
    cursor=conn.cursor()
    sql="""select gd.id, i.Fullname,r.rolename,g.name,gd.createddate,u.id from groupuserdetail gd join informationUser i on i.id=gd.iduser join rolegroupuser r on gd.idrolegroupuser=r.id
            join groupuser g on gd.idgroupuser=g.id join user_account u on u.id=i.id_useraccount where g.id=?"""
    value=(idgroup)
    cursor.execute(sql,value)
    userstemp=cursor.fetchall()
    conn.commit()
    conn.close()
    users=[(user[0],user[1],user[2],user[3],user[4],encode_id(user[5])) for user in userstemp]
    await form.load_data()
    form_method = await request.form() 
    if await form.is_valid() and 'updategroup' in form_method and form_method['updategroup']=='updategroup':
        groupuser = form.group
        
        conn=db.connection()
        cursor=conn.cursor()
        sql="""select i.Email,r.rolename,g.name from groupuserdetail gd join informationUser i on i.id=gd.iduser join rolegroupuser r on gd.idrolegroupuser=r.id
                join groupuser g on gd.idgroupuser=g.id where g.id=?"""
        value=(idgroup)
        cursor.execute(sql,value)
        notifyemail=cursor.fetchall()
        conn.commit()
        conn.close()

        conn=db.connection()
        cursor=conn.cursor()
        sql="update groupuser set name=?,alias=?,email=?,url=?,description=? where id=?"
        value=(groupuser,form.alias,form.email,
                form.url,form.description,idgroup)
        cursor.execute(sql,value)
        conn.commit()
        conn.close()
        messages=[('success',"update group user  is successful")]
        

        for notify in notifyemail:
            #send email notify
        
            html = "update group: "+ str(users[0][3]) 
            subject = "Group have been updated to group: "+ +str(groupuser) +",alias: " +str(form.alias.data)+",email: "+str(form.email.data)+",url: "+str(form.url.data)+",description: "+str(form.description.data)
            
            send_mail(notify[0], subject, html,2)
        #idgroup=idgroup,
        rolegroupvalue=rolegroupvalue
        return RedirectResponse(url=f"/adminpage/groupuserpage/updategroupuser/{idgroup}/{rolegroupvalue}",status_code=status.HTTP_302_FOUND)
    elif request.method=='POST'and 'adduser' in form_method and form_method['adduser']=='adduser':
        usersSelect=form_method["usersSelect"]
        grouprole=form_method["grouprole"]
        if usersSelect == '0' or grouprole == '0':
            messages=[('warn','please enter full information')]
            idgroup=idgroup,
            rolegroupvalue=rolegroupvalue
            return RedirectResponse(url=f"/adminpage/groupuserpage/updategroupuser/{idgroup}/{rolegroupvalue}",status_code=status.HTTP_302_FOUND)
            
        else:
            conn=db.connection()
            cursor=conn.cursor()
            sql="""
            SET NOCOUNT ON;
            DECLARE @id int;
            insert into groupuserdetail(iduser,idrolegroupuser,idgroupuser,createddate) values(?,?,?,GETDATE())
            SET @id = SCOPE_IDENTITY();            
            SELECT @id AS the_output;
            """
            value=(usersSelect,grouprole,idgroup)
            cursor.execute(sql,value)
            idgroupuserdetail=cursor.fetchone()
            conn.commit()
            conn.close()
            messages=[("success","add  user  is successful")]
            
            conn=db.connection()
            cursor=conn.cursor()
            sql="""select i.Email,r.rolename,g.name from groupuserdetail gd join informationUser i on i.id=gd.iduser join rolegroupuser r on gd.idrolegroupuser=r.id
                    join groupuser g on gd.idgroupuser=g.id where gd.id=?"""
            value=(idgroupuserdetail[0])
            cursor.execute(sql,value)
            notifyemail=cursor.fetchone()
            conn.commit()
            conn.close()
            #send email notify
            
            html = "You have been added to the group: "+ str(notifyemail[2]) +" with role: " +str(notifyemail[1])
            subject = "wellcome to "+ str(notifyemail[2])+" group"
            send_mail(notifyemail[0], subject, html,2) 
            
            rolegroupvalue=rolegroupvalue
            return RedirectResponse(url=f"/adminpage/groupuserpage/updategroupuser/{idgroup}/{rolegroupvalue}",status_code=status.HTTP_302_FOUND)
    elif request.method=='POST'and 'deletegroup' in form_method  and form_method['deletegroup']=='deletegroup':
        return RedirectResponse(url=f"/adminpage/groupuserpage/updategroup/deletegroupuser/{idgroup}",status_code=status.HTTP_302_FOUND)
    else:
        form.group=group[1]
        form.alias=group[4]
        form.email=group[5]
        form.url=group[6]
        form.description=group[7]

    
    # totp=pyotp.TOTP('adminroles')
    # totp=totp.now()
    # session['is_admin']=str(totp)
    context={
        "request":request,
        "current_user":current_user,
        "idgroup":idgroup,
        "image_path":file_path_default,
        "roleuser":roleuser.value,
        "usersSelect":usersSelect,
        "grouprole":grouprole,
        "users":users,
        "rolegroup":rolegroupvalue,
        #totp=str(totp),
        "form":form,
        "roleadmin" : _roleadmin,
        "image_path_admin":_image_path_admin,
        "fullname_admin" : _fullname_admin
    }
    return templates.TemplateResponse("admin/updategroupuser.html",context)
    
@admin.get('/adminpage/groupuserpage/updategroupuser/deleteuser/{idgroupuserdetail}/{idgroup}/{rolegroupvalue}')
def deleteuser(idgroupuserdetail,idgroup,rolegroupvalue,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="""select i.Email,r.rolename,g.name from groupuserdetail gd join informationUser i on i.id=gd.iduser join rolegroupuser r on gd.idrolegroupuser=r.id
            join groupuser g on gd.idgroupuser=g.id where gd.id=?"""
    value=(idgroupuserdetail)
    cursor.execute(sql,value)
    notifyemail=cursor.fetchone()
    conn.commit()
    conn.close()

    conn=db.connection()
    cursor=conn.cursor()
    sql="delete groupuserdetail where id=?"
    value=(idgroupuserdetail)
    cursor.execute(sql,value)
    conn.commit()
    conn.close()
    messages=[('success',"delete  user  is successful")]
   
    #send email notify
    
    html = "You have been removed from the group: "+ str(notifyemail[2]) +" with role: " +str(notifyemail[1])
    subject = "notice of member deletion from "+ str(notifyemail[2])+" group"
    send_mail(notifyemail[0], subject, html,2)
    return RedirectResponse(url=f"/adminpage/groupuserpage/updategroupuser/{idgroup}/{rolegroupvalue}",status_code=status.HTTP_302_FOUND)

@admin.get('/adminpage/groupuserpage/updategroup/deletegroupuser/{idgroup}')
def deletegroupuser(idgroup,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="""select i.Email,r.rolename,g.name from groupuserdetail gd join informationUser i on i.id=gd.iduser join rolegroupuser r on gd.idrolegroupuser=r.id
            join groupuser g on gd.idgroupuser=g.id where g.id=?"""
    value=(idgroup)
    cursor.execute(sql,value)
    notifyemail=cursor.fetchall()
    conn.commit()
    conn.close()

    conn=db.connection()
    cursor=conn.cursor()
    sql="""
            delete groupuserdetail where idgroupuser=?
            delete groupuser where id=?"""
    value=(idgroup,idgroup)
    cursor.execute(sql,value)
    conn.commit()
    conn.close()
    messages=[("success","removed  group user  is successful")]

    #send email notify
    for notify in notifyemail:
        html = "You have been removed from the group: "+ str(notify[2]) +" with role: " +str(notify[1])
        subject = "notice of member deletion from "+ str(notify[2])+" group"
        send_mail(notify[0], subject, html,2)
    return RedirectResponse(url="/adminpage/groupuserpage",status_code=status.HTTP_302_FOUND)

@admin.get('/adminpage/usersmanager/createemployee/{idinformation}',response_class=HTMLResponse)
async def createemployeeinfor_get(request:Request,idinformation,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from informationUserJob where idinformationuser=? and is_active=1"
    value=(decode_id(idinformation))
    cursor.execute(sql,value)
    informationjob=cursor.fetchone()
    conn.close()
    if informationjob is  None:
        form=Employeeinformation(request)
        userjob=informationUserJob(EmployeeNo=None,Companysitecode=None,Department=None,Directmanager=None,Workforcetype=None,Workingphone=None,Workingemail=None,
                    Bankaccount=None,Bankname=None,Taxcode=None,Socialinsurancecode=None,Healthinsurancecardcode=None,Registeredhospitalname=None,Registeredhospitalcode=None)
        temp=(0,' ')
        companysitecode=[]
        companysitecode.append(temp)
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from forextype "
        cursor.execute(sql)
        companysitecode_temp=cursor.fetchall()
        conn.close()
        for code in companysitecode_temp:
            temp=(code[0],code[1])
            companysitecode.append(temp)
    else:
        conn=db.connection()
        cursor=conn.cursor()
        sql="""select * from laborContract l join  informationUserJob ij on l.idinformationUserJob=ij.id join informationUser i on ij.idinformationuser=i.id 
        where i.id=? and l.is_active=1 and ij.is_active=1"""
        value=(decode_id(idinformation))
        cursor.execute(sql,value)
        labor=cursor.fetchone()  
        conn.close() 
        if labor is None:
            return RedirectResponse(url=f"/adminpage/usersmanager/createlaborcontract/{idinformation}",status_code=status.HTTP_302_FOUND)
        else:
            conn=db.connection()
            cursor=conn.cursor()
            sql="""select * from forexSalary f join  informationUserJob ij on f.idinformationUserJob=ij.id join informationUser i on ij.idinformationuser=i.id 
            where i.id=? and f.is_active=1 and ij.is_active=1"""
            value=(decode_id(idinformation))
            cursor.execute(sql,value)
            forex=cursor.fetchone()  
            conn.close()
            if forex is None:
                return RedirectResponse(url=f"/adminpage/usersmanager/createforexsalary/{idinformation}",status_code=status.HTTP_302_FOUND)
                
            else:
                
                messages=[('success','information job employee is exist')]
                return RedirectResponse(url="/adminpage/usersmanager",status_code=status.HTTP_302_FOUND)
    
    context={
        "request":request,
        "current_user":current_user,
        "image_path":file_path_default,
        "roleuser":roleuser.value,
        "roleadmin" : _roleadmin,
        "image_path_admin":_image_path_admin,
        "fullname_admin" : _fullname_admin,
        "informationuserid":idinformation,
        "userjob":userjob,
        "form":form,
        "companysitecode":companysitecode,
     
    }
    return templates.TemplateResponse("admin/admininformationuser.html",context)

@admin.post('/adminpage/usersmanager/createemployee/{idinformation}',response_class=HTMLResponse)
async def createemployeeinfor(request:Request,idinformation,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from informationUserJob where idinformationuser=? and is_active=1"
    value=(decode_id(idinformation))
    cursor.execute(sql,value)
    informationjob=cursor.fetchone()
    conn.close()
    if informationjob is  None:
        form=Employeeinformation(request)
        userjob=informationUserJob(EmployeeNo=None,Companysitecode=None,Department=None,Directmanager=None,Workforcetype=None,Workingphone=None,Workingemail=None,
                    Bankaccount=None,Bankname=None,Taxcode=None,Socialinsurancecode=None,Healthinsurancecardcode=None,Registeredhospitalname=None,Registeredhospitalcode=None)
        temp=(0,' ')
        companysitecode=[]
        companysitecode.append(temp)
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from forextype "
        cursor.execute(sql)
        companysitecode_temp=cursor.fetchall()
        conn.close()
        for code in companysitecode_temp:
            temp=(code[0],code[1])
            companysitecode.append(temp)
        await form.load_data()
        if await form.is_valid():
            form_method= await request.form()
            code=form_method['companysitecode']
            conn=db.connection()
            cursor=conn.cursor()
            sql="insert into informationUserJob values(?,?,?,?,?,?,?,?,?,?,?,?,?)"
            value=(code,form.department,form.directmanager,
                form.workfortype,form.Bankaccount,form.bankname,form.Taxcode,
                form.Socialinsurancecode,form.Healthinsurancecardcode,form.Registeredhospitalname,
                form.Registeredhospitalcode,decode_id(idinformation),1)
            cursor.execute(sql,value)
            conn.commit()
            conn.close()
            return RedirectResponse(url=f"/adminpage/usersmanager/createlaborcontract/{idinformation}",status_code=status.HTTP_302_FOUND)
    else:
        conn=db.connection()
        cursor=conn.cursor()
        sql="""select * from laborContract l join  informationUserJob ij on l.idinformationUserJob=ij.id join informationUser i on ij.idinformationuser=i.id 
        where i.id=? and l.is_active=1 and ij.is_active=1"""
        value=(decode_id(idinformation))
        cursor.execute(sql,value)
        labor=cursor.fetchone()  
        conn.close() 
        if labor is None:
            return RedirectResponse(url=f"/adminpage/usersmanager/createlaborcontract/{idinformation}",status_code=status.HTTP_302_FOUND)
        else:
            conn=db.connection()
            cursor=conn.cursor()
            sql="""select * from forexSalary f join  informationUserJob ij on f.idinformationUserJob=ij.id join informationUser i on ij.idinformationuser=i.id 
            where i.id=? and f.is_active=1 and ij.is_active=1"""
            value=(decode_id(idinformation))
            cursor.execute(sql,value)
            forex=cursor.fetchone()  
            conn.close()
            if forex is None:
                return RedirectResponse(url=f"/adminpage/usersmanager/createforexsalary/{idinformation}",status_code=status.HTTP_302_FOUND)
                
            else:
                
                messages=[('success','information job employee is exist')]
                return RedirectResponse(url="/adminpage/usersmanager",status_code=status.HTTP_302_FOUND)

@admin.get('/adminpage/usersmanager/createlaborcontract/{idinformation}',response_class=HTMLResponse)
async def createlaborcontract_get(request:Request,idinformation,current_user: User = Depends(get_current_user_from_token)):
    form=laborcontractForm(request)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id from informationUserJob where idinformationuser=? and is_active=1"
    value=(decode_id(idinformation))
    cursor.execute(sql,value)
    idinformationuserjob=cursor.fetchone()
    conn.commit()
    conn.close()
    context={
        "request":request,
        "current_user":current_user,
        "image_path":file_path_default,
        "roleuser":roleuser.value,
        "roleadmin" : _roleadmin,
        "image_path_admin":_image_path_admin,
        "fullname_admin" : _fullname_admin,
        "informationuserid":idinformation,
        "form":form,
       
    }
    return templates.TemplateResponse("admin/adminlaborcontract.html",context)

@admin.post('/adminpage/usersmanager/createlaborcontract/{idinformation}',response_class=HTMLResponse)
async def createlaborcontract(request:Request,idinformation,current_user: User = Depends(get_current_user_from_token)):
    form=laborcontractForm(request)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id from informationUserJob where idinformationuser=? and is_active=1"
    value=(decode_id(idinformation))
    cursor.execute(sql,value)
    idinformationuserjob=cursor.fetchone()
    conn.commit()
    conn.close()
    await form.load_data()
    if await form.is_valid():
        conn=db.connection()
        cursor=conn.cursor()
        sql="insert into laborContract values(null,?,?,?,?,?,?,?)"
        value=(form.Laborcontracttype,form.Laborcontractterm,form.Commencementdate,form.Position,form.Employeelevel,idinformationuserjob[0],1)
        cursor.execute(sql,value)
        conn.commit()
        conn.close()
        return RedirectResponse(url=f"/adminpage/usersmanager/createforexsalary/{idinformation}",status_code=status.HTTP_302_FOUND)
    context={
        "request":request,
        "current_user":current_user,
        "image_path":file_path_default,
        "roleuser":roleuser.value,
        "roleadmin" : _roleadmin,
        "image_path_admin":_image_path_admin,
        "fullname_admin" : _fullname_admin,
        "informationuserid":idinformation,
        "form":form
        
    }
    return templates.TemplateResponse("admin/adminlaborcontract.html",context)

@admin.get('/adminpage/usersmanager/createforexsalary/{idinformation}',response_class=HTMLResponse)
async def createforexsalary(request:Request,idinformation,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id,companysitecode from informationUserJob where idinformationuser=? and is_active=1"
    value=(decode_id(idinformation))
    cursor.execute(sql,value)
    idinformationuserjob=cursor.fetchone()
    conn.commit()
    conn.close()
    form=forexsalaryForm(request)
    form.forextype=idinformationuserjob[1]
    context={
        "request":request,
        "current_user":current_user,
        "image_path":file_path_default,
        "roleuser":roleuser.value,
        "roleadmin" : _roleadmin,
        "image_path_admin":_image_path_admin,
        "fullname_admin" : _fullname_admin,
        "informationuserid":idinformation,
        "form":form
        
    }
    return templates.TemplateResponse("admin/adminforexsalary.html",context)
    
   
@admin.post('/adminpage/usersmanager/createforexsalary/{idinformation}',response_class=HTMLResponse)
async def createforexsalary(request:Request,idinformation,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id,companysitecode from informationUserJob where idinformationuser=? and is_active=1"
    value=(decode_id(idinformation))
    cursor.execute(sql,value)
    idinformationuserjob=cursor.fetchone()
    conn.commit()
    conn.close()
    form=forexsalaryForm(request)
    form.forextype=idinformationuserjob[1]
    await form.load_data()
    if await form.is_valid():
        conn=db.connection()
        cursor=conn.cursor()
        sql="insert into forexSalary values(?,?,?,?,?,?,?,1)"
        value=(form.forextype,form.Annualsalary,form.Monthlysalary,
               form.Monthlysalaryincontract,form.Quaterlybonustarget,form.Annualbonustarget,idinformationuserjob[0])
        cursor.execute(sql,value)
        conn.commit()
        conn.close()

        conn=db.connection()
        cursor=conn.cursor()
        sql="select u.id from user_account u join informationUser i on u.id=i.id_useraccount where i.id=?"
        value=(decode_id(idinformation))
        cursor.execute(sql,value)
        idaccount=cursor.fetchone()
        conn.commit()
        conn.close()

        conn=db.connection()
        cursor=conn.cursor()
        sql="update user_account set role_id =1 where id=?"
        value=(idaccount[0])
        cursor.execute(sql,value)
        conn.commit()
        conn.close()
        messages=['success','create information job employee is successful']
        return RedirectResponse(url="/adminpage/usersmanager",status_code=status.HTTP_302_FOUND)
    context={
        "request":request,
        "current_user":current_user,
        "image_path":file_path_default,
        "roleuser":roleuser.value,
        "roleadmin" : _roleadmin,
        "image_path_admin":_image_path_admin,
        "fullname_admin" : _fullname_admin,
        "informationuserid":idinformation,
        "form":form,
        
    }
    return templates.TemplateResponse("admin/adminforexsalary.html",context)
    