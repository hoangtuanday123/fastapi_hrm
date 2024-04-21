import db
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from authentication.models import get_current_user_from_cookie,get_current_user_from_token
from authentication.models import User
from ultils import file_path_default,encode_id,decode_id
from globalvariable import readrights,idaccountadminmanager,rolegroup,roleadmin,fullname_adminsession,image_path_adminsession,roleuser
from core.forms import informationUserJob,laborContract,forexsalary,EmployeeRelativeForm
from core.models import employeeRelative
from .forms import Employeeinformation
templates = Jinja2Templates(directory="templates")
employee = APIRouter()

_image_path = ""
_fullname = ""
_roleuser = "employee"
_informationuserjobid = ""
_roleadmin = ""
_image_path_admin = ""
_fullname_admin = ""

@employee.get("/employeepage/{image_path}/{fullname}",tags=['employee'], response_class=HTMLResponse)

def employeepage(request:Request,image_path,fullname,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from informationUser where id_useraccount=?  "
    value=(decode_id(current_user.id))
    cursor.execute(sql,value)
    user=cursor.fetchone()
    conn.commit()
    conn.close()
    _image_path = image_path
    _fullname = fullname
    context={
        "request":request,
        "roleuser":"employee",
        "image_path":image_path,
        "fullname":fullname,
        "current_user":current_user,
        "idinformationuser":encode_id(user[0]),
        "informationuserid":encode_id(user[0])
    }
    return templates.TemplateResponse("employee/employeepage.html",context)

@employee.get("/informationuserjob/{informationuserid}",tags=['employee'],response_class=HTMLResponse)
async def informationuserjob_get(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    global _informationuserjobid, _image_path_admin,_fullname_admin,_fullname,_roleuser,_image_path
    
    
    #session['readrights']=None
    #readrights.value=None
    form=Employeeinformation(request)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select e.id,e.fullname from employeeRelative e join informationUser i on e.idinformationuser=i.id where i.id=?  "
    value=(decode_id(informationuserid))
    cursor.execute(sql,value)
    employeerelative_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    Employeerelative=[(person[0],person[1]) for person in employeerelative_temp]
    conn=db.connection()
    cursor=conn.cursor()
    sql="""
        select ei.id,e.fullname,e.Relationship,ei.col_Privateinsurance,ei.col_Additionalprivateinsurance,ei.col_Dependant,ei.col_Emergencycontact ,ei.col_Beneficiarycontact,e.id
        from employeerelative_informationuser ei join employeeRelative e on ei.idemployeerelative=e.id join informationUser i on i.id=ei.idinformationuser where i.id=?"""
    value=decode_id(informationuserid)
    cursor.execute(sql,value)
    temp=cursor.fetchall()
    conn.commit()
    conn.close() 
    temp1=[(user[0],user[1],user[2],user[3],user[8]) for user in temp if user[3]==True]
    temp2=[(user[0],user[1],user[2],user[4],user[8]) for user in temp if user[4]==True]
    temp3=[(user[0],user[1],user[2],user[5],user[8]) for user in temp if user[5]==True]
    temp4=[(user[0],user[1],user[2],user[6],user[8]) for user in temp if user[6]==True]
    temp5=[(user[0],user[1],user[2],user[7],user[8]) for user in temp if user[7]==True]

    conn=db.connection()
    cursor=conn.cursor()
    sql="""
        select i.*,iu.Email,iu.phone,u.id from informationUserJob i join informationUser 
        iu on i.idinformationuser=iu.id join user_account u on
        u.id=iu.id_useraccount where i.idinformationuser=? and i.is_active=1"""
    value=(decode_id(informationuserid))
    cursor.execute(sql,value)
    user=cursor.fetchone()
    conn.commit()
    conn.close()

    if user is not None:
        form.Bankaccount=str(user[5])
        form.bankname=str(user[6])
        form.Taxcode=str(user[8])
        form.Socialinsurancecode=str(user[9])
        form.Healthinsurancecardcode=str(user[10])
        form.Registeredhospitalcode=str(user[12])
        form.Registeredhospitalname=str(user[11])
        userjob=informationUserJob(EmployeeNo=user[0],Companysitecode=user[1],Department=user[2],Directmanager=user[3],Workforcetype=user[4],Workingphone=user[15],Workingemail=user[14],
            Bankaccount=user[5],Bankname=user[6],Taxcode=user[8],Socialinsurancecode=user[9],Healthinsurancecardcode=user[10],Registeredhospitalname=user[11],Registeredhospitalcode=user[12])
        _informationuserjobid = user[0]
    else:
        userjob=informationUserJob(EmployeeNo=None,Companysitecode=None,Department=None,Directmanager=None,Workforcetype=None,Workingphone=None,Workingemail=None,
            Bankaccount=None,Bankname=None,Taxcode=None,Socialinsurancecode=None,Healthinsurancecardcode=None,Registeredhospitalname=None,Registeredhospitalcode=None)
    print("id information user before redirect:" + str(informationuserid))   
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
        "temp2":temp2,
        "idaccount":idaccount,
        "readrights":readrights.value,
        "userjob":userjob,
        "form":form,
        "Employeerelative":Employeerelative,
        "temp1":temp1,
        "temp3":temp3,
        "temp4":temp4,
        "temp5":temp5,
    } 
    return templates.TemplateResponse("core/informationuserjob.html",context)
    
@employee.post("/informationuserjob/{informationuserid}",tags=['employee'],response_class=HTMLResponse)
async def informationuserjob(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    global _informationuserjobid, _image_path_admin,_fullname_admin,_fullname,_roleuser,_image_path
    
    
    #session['readrights']=None
    #readrights.value=None
    form=Employeeinformation(request)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select e.id,e.fullname from employeeRelative e join informationUser i on e.idinformationuser=i.id where i.id=?  "
    value=(decode_id(informationuserid))
    cursor.execute(sql,value)
    employeerelative_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    Employeerelative=[(person[0],person[1]) for person in employeerelative_temp]
    form_method=await request.form()
    if request.method=='POST' and form_method.get('Privateinsurance')=='Privateinsurance':
        
        result=addlist(informationuserid,form_method['Employeerelative1'],'Privateinsurance')
    
    if request.method=='POST' and form_method.get('Additionalprivateinsurance')=='Additionalprivateinsurance':
        
        result=addlist(informationuserid,form_method['Employeerelative2'],'Additionalprivateinsurance')

    if request.method=='POST' and form_method.get('Dependant')=='Dependant':
        result=addlist(informationuserid,request.form['Employeerelative3'],'Dependant')

    if request.method=='POST' and form_method.get('Emergencycontact')=='Emergencycontact':
        result=addlist(informationuserid,form_method['Employeerelative4'],'Emergencycontact')
    
    if request.method=='POST' and form_method.get('Beneficiarycontact')=='Beneficiarycontact':
        result=addlist(informationuserid,form_method['Employeerelative5'],'Beneficiarycontact')

    conn=db.connection()
    cursor=conn.cursor()
    sql="""
        select ei.id,e.fullname,e.Relationship,ei.col_Privateinsurance,ei.col_Additionalprivateinsurance,ei.col_Dependant,ei.col_Emergencycontact ,ei.col_Beneficiarycontact,e.id
        from employeerelative_informationuser ei join employeeRelative e on ei.idemployeerelative=e.id join informationUser i on i.id=ei.idinformationuser where i.id=?"""
    value=decode_id(informationuserid)
    cursor.execute(sql,value)
    temp=cursor.fetchall()
    conn.commit()
    conn.close() 
    temp1=[(user[0],user[1],user[2],user[3],user[8]) for user in temp if user[3]==True]
    temp2=[(user[0],user[1],user[2],user[4],user[8]) for user in temp if user[4]==True]
    temp3=[(user[0],user[1],user[2],user[5],user[8]) for user in temp if user[5]==True]
    temp4=[(user[0],user[1],user[2],user[6],user[8]) for user in temp if user[6]==True]
    temp5=[(user[0],user[1],user[2],user[7],user[8]) for user in temp if user[7]==True]

    conn=db.connection()
    cursor=conn.cursor()
    sql="""
        select i.*,iu.Email,iu.phone,u.id from informationUserJob i join informationUser 
        iu on i.idinformationuser=iu.id join user_account u on
        u.id=iu.id_useraccount where i.idinformationuser=? and i.is_active=1"""
    value=(decode_id(informationuserid))
    cursor.execute(sql,value)
    user=cursor.fetchone()
    conn.commit()
    conn.close()

    if user is not None:
        form.Bankaccount=str(user[5])
        form.bankname=str(user[6])
        form.Taxcode=str(user[8])
        form.Socialinsurancecode=str(user[9])
        form.Healthinsurancecardcode=str(user[10])
        form.Registeredhospitalcode=str(user[12])
        form.Registeredhospitalname=str(user[11])
        userjob=informationUserJob(EmployeeNo=user[0],Companysitecode=user[1],Department=user[2],Directmanager=user[3],Workforcetype=user[4],Workingphone=user[15],Workingemail=user[14],
            Bankaccount=user[5],Bankname=user[6],Taxcode=user[8],Socialinsurancecode=user[9],Healthinsurancecardcode=user[10],Registeredhospitalname=user[11],Registeredhospitalcode=user[12])
        _informationuserjobid = user[0]
    else:
        userjob=informationUserJob(EmployeeNo=None,Companysitecode=None,Department=None,Directmanager=None,Workforcetype=None,Workingphone=None,Workingemail=None,
            Bankaccount=None,Bankname=None,Taxcode=None,Socialinsurancecode=None,Healthinsurancecardcode=None,Registeredhospitalname=None,Registeredhospitalcode=None)
    print("id information user before redirect:" + str(informationuserid))   
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
        "temp2":temp2,
        "idaccount":idaccount,
        "readrights":readrights.value,
        "userjob":userjob,
        "form":form,
        "Employeerelative":Employeerelative,
        "temp1":temp1,
        "temp3":temp3,
        "temp4":temp4,
        "temp5":temp5,
        "idaccount":idaccount,
        "readrights":readrights.value
    } 
    return templates.TemplateResponse("core/informationuserjob.html",context)
    
def addlist(informationuserid,employeerelativeid,type):
    conn=db.connection()
    cursor=conn.cursor()
    sql="""
        SET NOCOUNT ON;
        DECLARE @result int;
        exec pr_employeerelative_informationuser @idinformationuser=?,@idemployeerelative=?,@type=?,@result=@result OUTPUT;
        SELECT @result AS the_output;
        """
    value=(decode_id(informationuserid),employeerelativeid,type)
    cursor.execute(sql,value)
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result[0]

@employee.get("/employeepage/informationuserjob/laborcontract/{informationuserjobid}/{informationuserid}",tags=['employee'],response_class=HTMLResponse)
def laborcontract(request:Request,informationuserjobid,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    global _image_path,_fullname,_roleuser,_informationuserjobid
    _roleadmin=""
    if rolegroup.value=='admin':
        _roleadmin="admin"
    idaccount=current_user.id
    if _roleadmin=="admin" :
        idaccount=idaccountadminmanager.value 
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from laborContract where idinformationUserJob=? and is_active=1"
    value=(informationuserjobid)
    cursor.execute(sql,value)
    contract=cursor.fetchone()
    conn.commit()
    conn.close()
    if contract is not None:
        contracttemp=laborContract(idcontract=contract[0],LaborcontractNo=contract[1],Laborcontracttype=contract[2],Laborcontractterm=contract[3],
                            Commencementdate=contract[4],Position=contract[5],Employeelevel=contract[6])
    else:
        contracttemp=laborContract(idcontract=None,LaborcontractNo=None,Laborcontracttype=None,Laborcontractterm=None,
                            Commencementdate=None,Position=None,Employeelevel=None)
    
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
        "contract":contracttemp,
        "informationuserjobid":_informationuserjobid,
        "idaccount":idaccount
    }
    return templates.TemplateResponse("core/contract.html",context)
    
@employee.get("/employeepage/informationuserjob/forexsalary/{informationuserjobid}/{informationuserid}",tags=['employee'],response_class=HTMLResponse)

def forexsalaryfunction(request:Request,informationuserjobid,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    global _image_path,_fullname,_roleuser,_informationuserjobid
    conn=db.connection()
    cursor=conn.cursor()
    sql="select f.*,ft.type from forexsalary f join forextype ft on f.forextypeid=ft.id where idinformationUserJob=? and is_active=1"
    value=(informationuserjobid)
    cursor.execute(sql,value)
    forexsalarytemp=cursor.fetchone()
    conn.commit()
    conn.close()
    if forexsalarytemp is not None:
        forexSalary=forexsalary(Forex=forexsalarytemp[9],Annualsalary=forexsalarytemp[2],Monthlysalary=forexsalarytemp[3],Monthlysalaryincontract=forexsalarytemp[4],
                                Quaterlybonustarget=forexsalarytemp[5],Annualbonustarget=forexsalarytemp[6])
    else:
        forexSalary=forexsalary(Forex=None,Annualsalary=None,Monthlysalary=None,Monthlysalaryincontract=None,
                                Quaterlybonustarget=None,Annualbonustarget=None)
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
        "forexSalary":forexSalary,
        "informationuserjobid":_informationuserjobid,
        "idaccount":idaccount
    }
    return templates.TemplateResponse("core/forexsalary.html",context)
    
@employee.get("/employeepage/informationuserjob/employeerelativelist/{informationuserid}",tags=['employee'],response_class=HTMLResponse)

def employeerelativelist(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from employeeRelative where idinformationuser=?"
    value=(decode_id(informationuserid))
    cursor.execute(sql,value)
    employeerelativetemp=cursor.fetchall()
    conn.commit()
    conn.close()
    employeerelativelist=[(relative[0],relative[8],relative[1]) for relative in employeerelativetemp ]
    if employeerelativelist is None:
        employeerelativelist =[]
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
        "employeerelativelist":employeerelativelist,
        "informationuserjobid":_informationuserjobid,
        "idaccount":idaccount,
        "readrights":readrights.value
        }
    return templates.TemplateResponse("core/employeeRelativeList.html",context)

@employee.get("/employeepage/informationuserjob/employeerelativelist/addemployeerelationship/{informationuserid}",tags=['employee'],response_class=HTMLResponse)

async def addemployeerelative_get(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    global _image_path, _fullname, _roleuser
    
    form = EmployeeRelativeForm(request)
    
    conn=db.connection()
    cursor=conn.cursor()
    sql="select u.id from user_account u join informationUser i on u.id=i.id_useraccount where i .id=?"
    value=(decode_id(informationuserid))
    cursor.execute(sql,value)
    idaccounttemp=cursor.fetchone()
    conn.commit()
    conn.close()
    idaccount=current_user.id
    if _roleadmin=="admin" :
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
        "form":form,
        "informationuserjobid":_informationuserjobid,
        "idaccount":idaccount,
        
        }
    return templates.TemplateResponse("core/addEmployeeRelationship.html",context)
    
 

@employee.post("/employeepage/informationuserjob/employeerelativelist/addemployeerelationship/{informationuserid}",tags=['employee'],response_class=HTMLResponse)

async def addemployeerelative(request:Request,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    global _image_path, _fullname, _roleuser
    
    form = EmployeeRelativeForm(request)
    
    conn=db.connection()
    cursor=conn.cursor()
    sql="select u.id from user_account u join informationUser i on u.id=i.id_useraccount where i .id=?"
    value=(decode_id(informationuserid))
    cursor.execute(sql,value)
    idaccounttemp=cursor.fetchone()
    conn.commit()
    conn.close()
    await form.load_data()
    
  
    if form.errors:
        print("Form validation errors:", form.errors)
    conn = db.connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO employeeRelative(Relationship, phone, email, contactaddress, career, idinformationuser, critizenIdentìicationNo,
        fullname, dateofbirth, placeofbirth, issuedon, address) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    value = (
        form.Relationship, form.phone, form.email, form.contactaddress, form.career, decode_id(informationuserid),
        form.citizenIdentificationNo, form.fullname, form.dateofbirth, form.placeofbirth, form.issued, form.address,
        )
    cursor.execute(sql, value)
    conn.commit()
    conn.close()
    messages=[('success','Insert employee relationship is successful')]
    return RedirectResponse(url=f"/employeepage/informationuserjob/employeerelativelist/{informationuserid}",status_code=status.HTTP_302_FOUND)
    
    
@employee.get("/employeepage/informationuserjob/employeerelativelist/delete/{employeerelativeid}/{informationuserid}",tags=['employee'])

def delete(employeerelativeid,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="""
    SET NOCOUNT ON;
    exec sp_delete_employeerelative @idemployeerelative=?;"""
    value=(employeerelativeid)
    cursor.execute(sql,value)
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/employeepage/informationuserjob/employeerelativelist/{informationuserid}",status_code=status.HTTP_302_FOUND)

@employee.get("/employeepage/informationuserjob/employeerelative/{employeerelativeid}/{informationuserid}/{idaccount}",tags=['employee'],response_class=HTMLResponse)
def employeerelative(request:Request,employeerelativeid,informationuserid,current_user: User = Depends(get_current_user_from_token)):
    global _image_path,_fullname,_roleuser        
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from employeeRelative where id=?"
    value=(employeerelativeid)
    cursor.execute(sql,value)
    employeerelativetemp=cursor.fetchone()
    form=EmployeeRelativeForm(request.form)
    if employeerelativetemp is not None:
        employeerelative=employeeRelative(id=employeerelativetemp[0],Relationship=employeerelativetemp[1],phone=employeerelativetemp[2],email=employeerelativetemp[3],
                                    contactaddress=employeerelativetemp[4],career=employeerelativetemp[5],citizenIdentificationNo=employeerelativetemp[7],
                                    fullname=employeerelativetemp[8],dateofbirth=employeerelativetemp[9],placeofbirth=employeerelativetemp[10],
                                    issuedon=employeerelativetemp[11],address=employeerelativetemp[12])
    else:
        employeerelative=employeeRelative(id=None,Relationship=None,phone=None,email=None,
                                    contactaddress=None,career=None,citizenIdentificationNo=None,
                                    fullname=None,dateofbirth=None,placeofbirth=None,
                                    issuedon=None,address=None)
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
        "employeerelative":employeerelative,
        "informationuserjobid":_informationuserjobid,
        "idaccount":idaccount,
        "employeerelativeid":employeerelativeid,
        "readrights":readrights.value
        }
    return templates.TemplateResponse("core/employeerelative.html",context)
    
@employee.get("/employeepage/informationuserjob/deleterelative/{informationuserid}/{employeerelativeid}/{type}",tags=['employee'])

def deleterelative(informationuserid,employeerelativeid,type,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="""
        SET NOCOUNT ON;
        exec pr_delete_employeerelative_informationuser @idinformationuser=?,@idemployeerelative=?,@type=?;
        """
    value=(decode_id(informationuserid),employeerelativeid,str(type))
    cursor.execute(sql,value)
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/informationuserjob/{informationuserid}",status_code=status.HTTP_302_FOUND)
    