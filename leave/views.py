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