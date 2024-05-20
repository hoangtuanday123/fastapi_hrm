import db
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from authentication.models import get_current_user_from_cookie,get_current_user_from_token
from authentication.models import User
from ultils import file_path_default,encode_id,decode_id
from datetime import datetime, timedelta
from ERP.forms import addtaskweeklytimesheetForm
templates = Jinja2Templates(directory="templates")
leave = APIRouter()

@leave.get("/LeaveManagement/leaveList",tags=['Leave management'], response_class=HTMLResponse)
async def leavelist(request:Request,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select p.projectid,p.projectname,pt.Name,p.startdate,p.status from project p join projecttype pt on pt.projecttypeid=p.projecttypeid where p.projecttypeid='PT2' and p.status=1"
    cursor.execute(sql)
    leave_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    leaves=[(project[0],project[1],project[2],project[3],project[4])for project in leave_temp]
    
    
    context={
        "request":request,
        "current_user":current_user,
        "leaves":leaves,
        "roleadmin" : request.cookies.get("roleadmin"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "fullname_admin" : request.cookies.get("fullname_adminsession"),
        "roleuser":request.cookies.get("roleuser"),
        "image_path": request.cookies.get("image_path_session"),
        "fullname": request.cookies.get("fullname_session")
    }
    return templates.TemplateResponse("leave/leaveManagement.html",context)

@leave.get("/LeaveManagement/createLeave",tags=['Leave management'], response_class=HTMLResponse)
async def createleave_get(request:Request,current_user: User = Depends(get_current_user_from_token)):
    form=addtaskweeklytimesheetForm(request)
    context={
        "request":request,
        "current_user":current_user,
        "form":form,
        "roleadmin" : request.cookies.get("roleadmin"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "fullname_admin" : request.cookies.get("fullname_adminsession"),
        "roleuser":request.cookies.get("roleuser"),
        "image_path": request.cookies.get("image_path_session"),
        "fullname": request.cookies.get("fullname_session")
    }
    return templates.TemplateResponse("leave/createleaveproject.html",context)

@leave.post("/LeaveManagement/createLeave",tags=['Leave management'], response_class=HTMLResponse)
async def createleave(request:Request,current_user: User = Depends(get_current_user_from_token)):
    form=addtaskweeklytimesheetForm(request)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select projecttypeid from projecttype where Name='Non-Project'"
    cursor.execute(sql)
    projecttype=cursor.fetchone()
    conn.commit()
    conn.close()
    await form.load_data()
    form_method=await request.form()
    if form.is_valid():
        conn=db.connection()
        cursor=conn.cursor()
        sql="""
            SET NOCOUNT ON;
            DECLARE @id int;
            insert into project(projecttypeid,startdate,projectname) values(?,GETDATE(),?)
            SET @id = SCOPE_IDENTITY();            
            SELECT @id AS the_output;"""
        values=(projecttype[0],form.project)
        cursor.execute(sql,values)
        idproject=cursor.fetchone()
        idproject="P"+str(idproject[0])
        conn.commit()
        conn.close()
        messages=[('success','create project '+form.project+" sucessfully")]
        return RedirectResponse(url=f"/ERP/createtaskandcomponent/{idproject}",status_code=status.HTTP_302_FOUND)
            
    context={
        "request":request,
        "current_user":current_user,
        "form":form,
        "roleadmin" : request.cookies.get("roleadmin"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "fullname_admin" : request.cookies.get("fullname_adminsession"),
        "roleuser":request.cookies.get("roleuser"),
        "image_path": request.cookies.get("image_path_session"),
        "fullname": request.cookies.get("fullname_session")
    }
    return templates.TemplateResponse("leave/createleaveproject.html",context)


@leave.get("/annualLeaveemployee",tags=['Leave management'], response_class=HTMLResponse)
async def annualLeaveemployee(request:Request,current_user: User = Depends(get_current_user_from_token)):
    current_date = datetime.now()

    # Lấy tháng và năm hiện tại
    #current_month = current_date.month
    current_year = current_date.year
    return RedirectResponse(url=f"/leave/annualLeaveemployee/{current_year}",status_code=status.HTTP_302_FOUND)

@leave.get("/leave/annualLeaveemployee/{year}",tags=["Leave management"],response_class=HTMLResponse)
async def annualleave_get(request:Request,year,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="""select d.id, p.projectid,p.projectname,t.name,c.name,d.startdate,d.enddate,d.total,d.statustimesheet 
from dayofftimesheet d join project p on d.projectid=p.projectid join taskproject t on d.taskid=t.id
LEFT join componentproject c on d.componentid=c.id join DATE da on d.startdate=da.Date join DATE da1 on d.enddate=da1.Date  where d.iduser=? and da.Year=?"""
    values=(decode_id(current_user.idinformationuser),year)
    cursor.execute(sql,values)
    annualeave_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    annualleavelist=[(project[0],project[1],project[2],project[3],project[4],
                      project[5],project[6],project[7],project[8])for project in annualeave_temp]
    context={
         "request":request,
        "current_user":current_user,
        "image_path":file_path_default,
        "roleuser":request.cookies.get("roleuser"),
        "fullname":request.cookies.get("fullname_session"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession"),
        "informationuserid":current_user.idinformationuser,
        # "informationuserjobid":_informationuserjobid,
        "idaccount":current_user.id,
        "readrights":request.cookies.get("readrights"),
        "idinformationuser":current_user.idinformationuser,
        "year":year,
        "annualleavelist":annualleavelist

        }
    
    return templates.TemplateResponse("leave/annualleavelist.html",context)

@leave.post("/leave/annualLeaveemployee/{year}",tags=["Leave management"],response_class=HTMLResponse)
async def annualleave(request:Request,year,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="""select d.id ,p.projectid,p.projectname,t.name,c.name,d.startdate,d.enddate,d.total,d.statustimesheet 
from dayofftimesheet d join project p on d.projectid=p.projectid join taskproject t on d.taskid=t.id
LEFT join componentproject c on d.componentid=c.id join DATE da on d.startdate=da.Date join DATE da1 on d.enddate=da1.Date  where d.iduser=? and da.Year=? """
    values=(decode_id(current_user.idinformationuser),year)
    cursor.execute(sql,values)
    annualeave_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    annualleavelist=[(project[0],project[1],project[2],project[3],project[4],
                      project[5],project[6],project[7],project[8])for project in annualeave_temp]
    form_method=await request.form()
    if "yearform" in form_method and form_method.get("yearform")=="yearform":
        return RedirectResponse(url=f"/leave/annualLeaveemployee/{form_method.get("year")}",status_code=status.HTTP_302_FOUND)
    elif "addtasks" in form_method and form_method.get("addtasks")=="addtasks":
        return RedirectResponse(url=f"/annualleave_addtask/{current_user.idinformationuser}/{year}",status_code=status.HTTP_302_FOUND)
    elif 'removetasks' in form_method and form_method['removetasks']=='removetasks':
        selecttiontasks=form_method.getlist('checkbox')
        
        for select in selecttiontasks:
            removetasks(select)
        message=[('success','remove task is successfully')]
        return RedirectResponse(url=f"/leave/annualLeaveemployee/{year}",status_code=status.HTTP_302_FOUND)
    elif 'recalltasks'in form_method and form_method.get('recalltasks')=='recalltasks':
        selecttiontasks=form_method.getlist('checkbox')
        for list in selecttiontasks:
            recalltasks(list)
        
        message=[('success','submit tasks is successfull')]
        return RedirectResponse(url=f"/leave/annualLeaveemployee/{year}",status_code=status.HTTP_302_FOUND)
    elif 'savetasks' in form_method and form_method['savetasks']=='savetasks':
        selecttiontasks=form_method.getlist('checkbox')
        for id in selecttiontasks:
            savetasks(id)
        message=[('success','update progress is sucessfull')]
        return RedirectResponse(url=f"/leave/annualLeaveemployee/{year}",status_code=status.HTTP_302_FOUND)
    elif 'submittasks'in form_method and form_method.get('submittasks')=='submittasks':
        selecttiontasks=form_method.getlist('checkbox')
        for id in selecttiontasks:
            submittasks(id)
        message=[('success','submit tasks is sucessfull')]
        return RedirectResponse(url=f"/leave/annualLeaveemployee/{year}",status_code=status.HTTP_302_FOUND)
    context={
         "request":request,
        "current_user":current_user,
        "image_path":file_path_default,
        "roleuser":request.cookies.get("roleuser"),
        "fullname":request.cookies.get("fullname_session"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession"),
        "informationuserid":current_user.idinformationuser,
        # "informationuserjobid":_informationuserjobid,
        "idaccount":current_user.id,
        "readrights":request.cookies.get("readrights"),
        "idinformationuser":current_user.idinformationuser,
        "year":year,
        "annualleavelist":annualleavelist

        }
    
    return templates.TemplateResponse("leave/annualleavelist.html",context)

def removetasks(dayoffid):
    conn=db.connection()
    cursor=conn.cursor()
    sql="delete dayofftimesheet where id=?"
    cursor.execute(sql,dayoffid)
    conn.commit()
    conn.close()

def recalltasks(select):
    conn=db.connection()
    cursor=conn.cursor()
    sql="update dayofftimesheet set statustimesheet='recalling' where id=? and statustimesheet !='saved' and statustimesheet !='approval'"
    cursor.execute(sql,select)
    conn.commit()
    conn.close()

def savetasks(id):
  
    conn=db.connection()
    cursor=conn.cursor()
    sql="update dayofftimesheet set statustimesheet='saved' where id=? and statustimesheet !='pending approval' and statustimesheet !='approval'"
    value=(id)
    cursor.execute(sql,value)
    conn.commit()
    conn.close()
        
def submittasks(id):
    conn=db.connection()
    cursor=conn.cursor()
    sql="update dayofftimesheet set statustimesheet='pending approval' where id=? and statustimesheet !='pending approval' and statustimesheet!='initialization' and statustimesheet !='approval' "
    cursor.execute(sql,id)
    conn.commit()
    conn.close()      
  

@leave.get("/annualleave_addtask/{iduser}/{year}",tags=['Leave management'],status_code=status.HTTP_302_FOUND)
async def addtask_get(request:Request,iduser,year,current_user: User = Depends(get_current_user_from_token)): 
        #form=addtaskweeklytimesheetForm(request)
    conn=db.connection()
    cursor=conn.cursor()
    sql="""
    select p.projectid,p.projectname from project p join groupuser g on p.projectteamid=g.id 
    join groupuserdetail gd on gd.idgroupuser=g.id join projecttype pt on pt.projecttypeid=p.projecttypeid  where  gd.iduser=? and p.status=1 and pt.Name='Non-Project'
        """
    value=(decode_id(iduser))
    cursor.execute(sql,value)
    project_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    projects=[(project[0],project[1])for project in project_temp]
   
    conn=db.connection()
    cursor=conn.cursor()
    sql="select t.id,t.name from taskproject t join project p on t.projectid=p.projectid where t.projectid=? and p.status=1"
    value=(projects[0][0])
    cursor.execute(sql,value)
    tasks_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    tasks = [(task[0],task[1])for task in tasks_temp]
    conn=db.connection()
    cursor=conn.cursor()
    sql="select c.id,c.name from componentproject c join project p on c.projectid=p.projectid where c.projectid=? and p.status=1"
    value=(projects[0][0])
    cursor.execute(sql,value)
    components_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    components =[(component[0],component[1])for component in components_temp]
    context={
        "request":request,
        "current_user":current_user,
        "roleadmin" : request.cookies.get("roleadmin"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "fullname_admin" : request.cookies.get("fullname_adminsession"),
        "projects":projects,
        "tasks":tasks,
        "components":components,
        "roleuser":request.cookies.get("roleuser"),
        "image_path": request.cookies.get("image_path_session"),
        "fullname": request.cookies.get("fullname_session")
    }
    return templates.TemplateResponse("leave/addannualleave.html",context)     


@leave.post("/annualleave_addtask/{iduser}/{year}",tags=['Leave management'],status_code=status.HTTP_302_FOUND)
async def addtask(request:Request,iduser,year,current_user: User = Depends(get_current_user_from_token)): 
    #form=addtaskweeklytimesheetForm(request)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select p.projectid,p.projectname from project p join groupuser g on p.projectteamid=g.id join groupuserdetail gd on gd.idgroupuser=g.id where  gd.iduser=? and p.status=1"
    value=(decode_id(iduser))
    cursor.execute(sql,value)
    project_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    projects=[(project[0],project[1])for project in project_temp]
    
    conn=db.connection()
    cursor=conn.cursor()
    sql="select t.id,t.name from taskproject t join project p on t.projectid=p.projectid where t.projectid=? and p.status=1"
    value=(projects[0][0])
    cursor.execute(sql,value)
    tasks_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    tasks = [(task[0],task[1])for task in tasks_temp]
    
    conn=db.connection()
    cursor=conn.cursor()
    sql="select c.id,c.name from componentproject c join project p on c.projectid=p.projectid where c.projectid=? and p.status=1"
    value=(projects[0][0])
    cursor.execute(sql,value)
    components_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    components =[(component[0],component[1])for component in components_temp]
    form_method=await request.form()
    if request.method=="POST":
        startdate = datetime.strptime(form_method['startdate'], '%Y-%m-%d')
        enddate = datetime.strptime(form_method['enddate'], '%Y-%m-%d')
        total_days = (enddate - startdate).days
        if total_days>0:
            if 'component' in form_method and  form_method['component'] is not None:
                conn=db.connection()
                cursor=conn.cursor()
                sql="insert into dayofftimesheet(iduser,projectid,componentid,taskid,startdate,enddate,statustimesheet,total) values(?,?,?,?,?,?,'initialization',?)"
                value=(decode_id(iduser),form_method['project'],form_method['component'],form_method['task'],form_method['startdate'],form_method['enddate'],total_days)
                cursor.execute(sql,value)
                conn.commit()
                conn.close()
            else:
                conn=db.connection()
                cursor=conn.cursor()
                sql="insert into dayofftimesheet(iduser,projectid,componentid,taskid,startdate,enddate,statustimesheet,total) values(?,?,?,?,?,?,'initialization',?)"
                value=(decode_id(iduser),form_method['project'],None,form_method['task'],form_method['startdate'],form_method['enddate'],total_days)
                cursor.execute(sql,value)
                conn.commit()
                conn.close()
            messages=[('success','add task weekly timesheet is successfull')]
            return RedirectResponse(url=f"/leave/annualLeaveemployee/{year}",status_code=status.HTTP_302_FOUND)
        return RedirectResponse(url=f"/annualleave_addtask/{iduser}/{year}",status_code=status.HTTP_302_FOUND)
    
@leave.get("/annualleaveadmin_view",tags=['Leave management'],status_code=status.HTTP_302_FOUND)
async def annualleaveadmin_view(request:Request,current_user: User = Depends(get_current_user_from_token)): 
    current_date = datetime.now()
    curent_year= current_date.year
    curent_year=str(curent_year)
    #return (curent_year)
    return RedirectResponse(url=f"/annualleave_view/{curent_year}",status_code=status.HTTP_302_FOUND)

@leave.get("/annualleave_view/{year}",tags=['Leave management'],status_code=status.HTTP_302_FOUND)
async def annualleave_view_get(request:Request,year,current_user: User = Depends(get_current_user_from_token)): 
    current_date = datetime.now()
    # Extract the current year
    curent_year= current_date.year
    if str(curent_year)==year:
        year==curent_year
    conn=db.connection()
    cursor=conn.cursor()
    sql="""select d.id ,p.projectid,p.projectname,t.name,c.name,d.startdate,d.enddate,d.total,d.statustimesheet 
from dayofftimesheet d join project p on d.projectid=p.projectid join taskproject t on d.taskid=t.id
LEFT join componentproject c on d.componentid=c.id join DATE da on d.startdate=da.Date join DATE da1 on d.enddate=da1.Date  where  da.Year=? """
    values=(year)
    cursor.execute(sql,values)
    annualeave_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    annualleavelist=[(project[0],project[1],project[2],project[3],project[4],
                      project[5],project[6],project[7],project[8])for project in annualeave_temp]
    context={
        "request":request,
        "current_user":current_user,
        "roleadmin" : request.cookies.get("roleadmin"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "fullname_admin" : request.cookies.get("fullname_adminsession"),
        "annualleavelist":annualleavelist,
        "year":year
    }
    return templates.TemplateResponse("leave/annualleaveadminview.html",context)

@leave.post("/annualleave_view/{year}",tags=['leave'],status_code=status.HTTP_302_FOUND)
async def annualleave_view(request:Request,year,current_user: User = Depends(get_current_user_from_token)): 
    form_method=await request.form()
    if "yearform" in form_method and form_method.get("yearform")=="yearform":
       return RedirectResponse(url=f"/annualleave_view/{form_method["year"]}",status_code=status.HTTP_302_FOUND)
    elif "approvals" in form_method and form_method.get('approvals')=="approvals":
        sellectionItem=form_method.getlist("checkbox")
        approvaldayoff(sellectionItem)
        return RedirectResponse(url=f"/annualleave_view/{year}",status_code=status.HTTP_302_FOUND)
    elif "pendingapprovals" in form_method and form_method.get('pendingapprovals')=="pendingapprovals":
        sellectionItem=form_method.getlist("checkbox")
        pendingapprovaldayoff(sellectionItem)
        return RedirectResponse(url=f"/annualleave_view/{year}",status_code=status.HTTP_302_FOUND)


def approvaldayoff(selectionItem):
    for item in selectionItem:
        conn=db.connection()
        cursor=conn.cursor()
        sql="update dayofftimesheet set statustimesheet='approval' where id=?"
        cursor.execute(sql,item)
        conn.commit()
        conn.close()

def pendingapprovaldayoff(selectionItem):
    for item in selectionItem:
        conn=db.connection()
        cursor=conn.cursor()
        sql="update dayofftimesheet set statustimesheet='pending approval' where id=?"
        cursor.execute(sql,item)
        conn.commit()
        conn.close()

