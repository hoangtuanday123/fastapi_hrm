import db
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse,JSONResponse
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from authentication.models import get_current_user_from_cookie,get_current_user_from_token
from authentication.models import User
from ultils import file_path_default,encode_id,decode_id
from datetime import datetime, timedelta
from.forms import addtaskweeklytimesheetForm
from globalvariable import image_path_adminsession,fullname_adminsession,roleuser,roleadmin,fullname_session,image_path_session

_role_user = ""
_roleadmin = "admin"
_image_path_admin = ""
_fullname_admin = ""
_image_path = ""
_fullname = ""

ERP=APIRouter()
templates = Jinja2Templates(directory="templates")
def calendar(year):
    year=int(year)
    start_date = datetime(year, 1, 1)
    weeks_in_year = []
    while start_date.year == year:
        start_of_week = start_date - timedelta(days=start_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        week_dates = [
            {"date": (start_of_week + timedelta(days=i)).strftime("%Y-%m-%d"),
            "day_of_week": (start_of_week + timedelta(days=i)).strftime("%A")} for i in range(7)]
        weeks_in_year.append({
            "week_number": start_date.isocalendar()[1],
            "start_of_week": start_of_week.strftime("%Y-%m-%d"),
            "end_of_week": end_of_week.strftime("%Y-%m-%d"),
            "week_dates": week_dates
        })

        start_date += timedelta(days=7)
    weeks_in_year.pop()
    return weeks_in_year

@ERP.get("/ERP/projectlist",tags=['ERP'], response_class=HTMLResponse)
def projectlist(request:Request,current_user: User = Depends(get_current_user_from_token)):
    global _image_path_admin,_fullname_admin
    conn=db.connection()
    cursor=conn.cursor()
    sql="""select p.projectid,p.projectname,pt.Name,i.Fullname,g.name,
    p.startdate,p.endate,p.status,pt.projecttypeid from project p join projecttype 
    pt on p.projecttypeid=pt.projecttypeid join informationUser i 
    on p.managerid=i.id join groupuser g on p.projectteamid=g.id where p.status=1"""
    cursor.execute(sql)
    projects_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    projects=[(project[0],project[1],project[2],project[3],project[4],
               project[5],project[6],project[7],project[8])for project in projects_temp]
    context={
        "request":request,
        "current_user":current_user,
        "projects":projects,
        "roleadmin" : _roleadmin,
        "image_path_admin":image_path_adminsession.value,
        "fullname_admin" : fullname_adminsession.value,
        "roleuser":roleuser.value,
        "image_path": image_path_session.value,
        "fullname": fullname_session.value
    }
    return templates.TemplateResponse("ERP/projectlistadmin.html",context)
    #return render_template("ERP/projectlistadmin.html",projects=projects)

@ERP.get("/ERP/createproject",tags=['ERP'], response_class=HTMLResponse)
async def createproject_get(request:Request,current_user: User = Depends(get_current_user_from_token)):
    global _image_path_admin,_fullname_admin
    form=addtaskweeklytimesheetForm(request)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select projecttypeid,name from projecttype"
    cursor.execute(sql)
    projecttype_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    projecttype=[]
    projecttype.append((0,'null'))
    for project in projecttype_temp:
        projecttype.append((project[0],project[1]))
    context={
        "request":request,
        "current_user":current_user,
        "form":form,
        "projecttype":projecttype,
        "roleadmin" : _roleadmin,
        "image_path_admin":image_path_adminsession.value,
        "fullname_admin" : fullname_adminsession.value,
        "roleuser":roleuser.value,
        "image_path": image_path_session.value,
        "fullname": fullname_session.value
    }
    return templates.TemplateResponse("ERP/createprojectadmin.html",context)

@ERP.post("/ERP/createproject",tags=['ERP'], response_class=HTMLResponse)
async def createproject(request:Request,current_user: User = Depends(get_current_user_from_token)):
    global _image_path_admin,_fullname_admin
    form=addtaskweeklytimesheetForm(request)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select projecttypeid,name from projecttype"
    cursor.execute(sql)
    projecttype_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    projecttype=[]
    projecttype.append((0,'null'))
    for project in projecttype_temp:
        projecttype.append((project[0],project[1]))
    await form.load_data()
    form_method=await request.form()
    if form.is_valid():
        if form_method['projecttype']!='0':
            conn=db.connection()
            cursor=conn.cursor()
            sql="""
                SET NOCOUNT ON;
                DECLARE @id int;
                insert into project(projecttypeid,startdate,endate,projectname) values(?,GETDATE(),?,?)
                SET @id = SCOPE_IDENTITY();            
                SELECT @id AS the_output;"""
            values=(form_method['projecttype'],form.enddate,form.project)
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
        "projecttype":projecttype,
        "roleadmin" : _roleadmin,
        "image_path_admin":image_path_adminsession.value,
        "fullname_admin" : fullname_adminsession.value,
        "roleuser":roleuser.value,
        "image_path": image_path_session.value,
        "fullname": fullname_session.value
    }
    return templates.TemplateResponse("ERP/createprojectadmin.html",context)


@ERP.get("/ERP/createtaskandcomponent/{idproject}",tags=['ERP'],response_class=HTMLResponse)
async def createtaskandcomponent_get(request:Request,idproject,current_user: User = Depends(get_current_user_from_token)):
    form=addtaskweeklytimesheetForm(request)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from taskproject where projectid=?"
    value=(idproject)
    cursor.execute(sql,value)
    tasks_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    tasks=[(task[0],task[1],task[2])for task in tasks_temp]

    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from componentproject where projectid=?"
    value=(idproject)
    cursor.execute(sql,value)
    components_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    components=[(component[0],component[1],component[2])for component in components_temp]
    context={
        "request":request,
        "current_user":current_user,
        "roleadmin" : _roleadmin,
        "image_path_admin":image_path_adminsession.value,
        "fullname_admin" : fullname_adminsession.value,
        "form":form,
        "idproject":idproject,
        "tasks":tasks,
        "components":components,
        "roleuser":roleuser.value,
        "image_path": image_path_session.value,
        "fullname": fullname_session.value

    }
    return templates.TemplateResponse("ERP/addtaskscomponentprojectadmin.html",context)

@ERP.post("/ERP/createtaskandcomponent/{idproject}",tags=['ERP'],response_class=HTMLResponse)
async def createtaskandcomponent(request:Request,idproject,current_user: User = Depends(get_current_user_from_token)):
    form=addtaskweeklytimesheetForm(request)
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from taskproject where projectid=?"
    value=(idproject)
    cursor.execute(sql,value)
    tasks_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    tasks=[(task[0],task[1],task[2])for task in tasks_temp]

    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from componentproject where projectid=?"
    value=(idproject)
    cursor.execute(sql,value)
    components_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    components=[(component[0],component[1],component[2])for component in components_temp]
    form_method= await request.form()
    await form.load_data()
    if request.method=='POST' and 'taskbutton' in  form_method and form_method['taskbutton']=='taskbutton':
        conn=db.connection()
        cursor=conn.cursor()
        sql="insert into taskproject(name,createdate,projectid) values(?,GETDATE(),?)"
        value=(form.task,idproject)
        cursor.execute(sql,value)
        conn.commit()
        conn.close()
        return RedirectResponse(url=f"/ERP/createtaskandcomponent/{idproject}",status_code=status.HTTP_302_FOUND)
        
    if request.method=='POST' and 'componentbutton' in form_method and form_method['componentbutton']=='componentbutton':
        conn=db.connection()
        cursor=conn.cursor()
        sql="insert into componentproject(name,createdate,projectid) values(?,GETDATE(),?)"
        value=(form.component,idproject)
        cursor.execute(sql,value)
        conn.commit()
        conn.close()
        return RedirectResponse(url=f"/ERP/createtaskandcomponent/{idproject}",status_code=status.HTTP_302_FOUND)
    context={
        "request":request,
        "current_user":current_user,
        "roleadmin" : _roleadmin,
        "image_path_admin":image_path_adminsession.value,
        "fullname_admin" : fullname_adminsession.value,
        "form":form,
        "idproject":idproject,
        "tasks":tasks,
        "components":components,
        "roleuser":roleuser.value,
        "image_path": image_path_session.value,
        "fullname": fullname_session.value

    }
    return templates.TemplateResponse("ERP/addtaskscomponentprojectadmin.html",context)

@ERP.get("/ERP/deleteTask/{idproject}/{idtask}",tags=['ERP'])
def deleteTask(idproject,idtask):
    conn=db.connection()
    cursor=conn.cursor()
    sql="delete taskproject where id=?"
    value=(idtask)
    cursor.execute(sql,value)
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/ERP/createtaskandcomponent/{idproject}",status_code=status.HTTP_302_FOUND)

@ERP.get("/ERP/deleteComponent/{idproject}/{idcomponent}",tags=['ERP'])
def deleteComponent(idproject,idcomponent):
    conn=db.connection()
    cursor=conn.cursor()
    sql="delete componentproject where id=?"
    value=(idcomponent)
    cursor.execute(sql,value)
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/ERP/createtaskandcomponent/{idproject}",status_code=status.HTTP_302_FOUND)

@ERP.get("/ERP/assigngroup/{idproject}",tags=['ERP'],response_class=HTMLResponse)
async def assigngroupproject_get(request:Request,idproject,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id,name from groupuser"
    cursor.execute(sql)
    groups_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    groups=[(group[0],group[1])for group in groups_temp]
    context={
        "request":request,
        "current_user":current_user,
        "roleadmin" : _roleadmin,
        "image_path_admin":image_path_adminsession.value,
        "fullname_admin" : fullname_adminsession.value,
                "roleuser":roleuser.value,
        "image_path": image_path_session.value,
        "fullname": fullname_session.value,
        "groups":groups
    }
    return templates.TemplateResponse("ERP/assigngroupprojectadmin.html",context)

@ERP.post("/ERP/assigngroup/{idproject}",tags=['ERP'],response_class=HTMLResponse)
async def assigngroupproject(request:Request,idproject,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select id,name from groupuser"
    cursor.execute(sql)
    groups_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    groups=[(group[0],group[1])for group in groups_temp]
    form=await request.form()
    
    if request.method=="POST":
        conn=db.connection()
        cursor=conn.cursor()
        sql="select g.id,gd.iduser from groupuser g join groupuserdetail gd on g.id=gd.idgroupuser join rolegroupuser rg on rg.id=gd.idrolegroupuser where rg.rolename='manager' and g.id=?"
        value=(form["group"])
        cursor.execute(sql,value)
        groups_temp1=cursor.fetchone()
        conn.commit()
        conn.close()
        if groups_temp1 is None:
            message=[('warn','group dont have manager role')]
            return RedirectResponse(url=f"/ERP/assigngroup/{idproject}",status_code=status.HTTP_302_FOUND)
        conn=db.connection()
        cursor=conn.cursor()
        sql="update project set managerid=?,projectteamid=? where projectid=?"
        value=(int(groups_temp1[1]),int(groups_temp1[0]),idproject)
        cursor.execute(sql,value)
        conn.commit()
        conn.close()
        return RedirectResponse(url="/ERP/projectlist",status_code=status.HTTP_302_FOUND)
    context={
        "request":request,
        "current_user":current_user,
        "roleadmin" : _roleadmin,
        "image_path_admin":image_path_adminsession.value,
        "fullname_admin" : fullname_adminsession.value,
        "groups":groups,
                "roleuser":roleuser.value,
        "image_path": image_path_session.value,
        "fullname": fullname_session.value
    }
    return templates.TemplateResponse("ERP/assigngroupprojectadmin.html",context)


@ERP.get("/ERP/updateproject/{idproject}",tags=['ERP'],response_class=HTMLResponse)
async def updateproject_get(request:Request,idproject,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select projecttypeid,name from projecttype"
    cursor.execute(sql)
    projecttype_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    projecttype=[(project[0],project[1])for project in projecttype_temp]

    conn=db.connection()
    cursor=conn.cursor()
    sql="select p.projectid,p.projectname,pt.projecttypeid,pt.Name from project p join projecttype pt on p.projecttypeid=pt.projecttypeid where p.projectid=?"
    value=(idproject)
    cursor.execute(sql,value)
    project=cursor.fetchone()
    conn.commit()
    conn.close()
    context={
        "request":request,
        "current_user":current_user,
        "roleadmin" : _roleadmin,
        "image_path_admin":image_path_adminsession.value,
        "fullname_admin" : fullname_adminsession.value,
        "projecttype":projecttype,
        "projectname":project[1],
        "projecttypeid":project[2],
        "projecttypename":project[3],
        "idproject":idproject,
                "roleuser":roleuser.value,
        "image_path": image_path_session.value,
        "fullname": fullname_session.value
    } 
    return templates.TemplateResponse("ERP/updateprojectadmin.html",context)   
    

@ERP.post("/ERP/updateproject/{idproject}",tags=['ERP'],response_class=HTMLResponse)
async def updateproject(request:Request,idproject,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select projecttypeid,name from projecttype"
    cursor.execute(sql)
    projecttype_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    projecttype=[(project[0],project[1])for project in projecttype_temp]

    conn=db.connection()
    cursor=conn.cursor()
    sql="select p.projectid,p.projectname,pt.projecttypeid,pt.Name from project p join projecttype pt on p.projecttypeid=pt.projecttypeid where p.projectid=?"
    value=(idproject)
    cursor.execute(sql,value)
    project=cursor.fetchone()
    conn.commit()
    conn.close()
    form=await request.form()
    if request.method=="POST":
        conn=db.connection()
        cursor=conn.cursor()
        sql="update project set projectname=?,projecttypeid=? where projectid=?"
        value=(form["projectname"],form["projecttype"],idproject)
        cursor.execute(sql,value)
        conn.commit()
        conn.close()
        #flash("update is successful")
        messages=[('success','update is successful')]
        return RedirectResponse(url=f"/ERP/updateproject/{idproject}",status_code=status.HTTP_302_FOUND)

    context={
        "request":request,
        "current_user":current_user,
        "roleadmin" : _roleadmin,
        "image_path_admin":image_path_adminsession.value,
        "fullname_admin" : fullname_adminsession.value,
        "projecttype":projecttype,
        "projectname":project[1],
        "projecttypeid":project[2],
        "projecttypename":project[3],
        "idproject":idproject,
                "roleuser":roleuser.value,
        "image_path": image_path_session.value,
        "fullname": fullname_session.value
    } 
    return templates.TemplateResponse("ERP/updateprojectadmin.html",context)   
    
@ERP.get("/ERP/deleteproject/{idproject}",tags=['ERP'])
def deleteproject(idproject,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="update project set status=0 where projectid=?"
    value=(idproject)
    cursor.execute(sql,value)
    conn.commit()
    conn.close()
    return RedirectResponse(url="/ERP/projectlist",status_code=status.HTTP_302_FOUND)

@ERP.get("/WeeklyTimesheet/{iduser}",tags=['ERP'],response_class=HTMLResponse)
def calendertimesheet_get(request:Request,iduser,current_user: User = Depends(get_current_user_from_token)):
    current_datetime = datetime.now()
    year=current_datetime.year
    weeknum = current_datetime.isocalendar()[1]
    # if request.method=='POST' and request.form.get('yearform')=='yearform':
    #     year=request.form['year']
    #weeks_in_year=calendar(year)
    return RedirectResponse(url=f"/WeeklyTimesheet/{iduser}/{year}/{weeknum}",status_code=status.HTTP_302_FOUND)
    
@ERP.get("/WeeklyTimesheet/{iduser}/{year}/{weeknum}",tags=['ERP'],response_class=HTMLResponse)
async def weeklytimesheet_get(request:Request,iduser,year,weeknum,current_user: User = Depends(get_current_user_from_token)):
    weeks_in_year=calendar(year)
    
    weekdates=[]
    for week in weeks_in_year:
        if str(week['week_number']) == str(weeknum):
            weekdates = [str(date_obj['date']) for date_obj in week['week_dates']]
            break
            
    conn=db.connection()
    cursor=conn.cursor()
    sql="""select p.projectid,pt.Name,p.projectname,c.name,t.name,w.mon,w.tue,w.wed,w.thu,w.fri,w.sat,w.sun,w.statustimesheet,w.note,w.id,w.progress
 from weeklytimesheet w join project p on w.projectid=p.projectid join
 projecttype pt on pt.projecttypeid=p.projecttypeid join componentproject c on w.componentid =c.id join 
 taskproject t on w.taskid=t.id join DATE d on d.Date=w.Date where d.Year=? and d.WeekNumber=? and w.iduser=? and w.status=1"""
    values=(year,weeknum,decode_id(iduser))
    cursor.execute(sql,values)
    weeklytimesheet_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    weeklytimesheetvalues=[(project[0],project[1],project[2],project[3],project[4],project[5],
                            project[6],project[7],project[8],project[9],project[10],project[11],
                            project[12],project[13],project[14],project[15])for project in weeklytimesheet_temp]
    #listweeklytimesheetid=[(project[14])for project in weeklytimesheet_temp]
    selecttiontasks=[]
    timesheetstatus=None
    if weeklytimesheetvalues !=[]:
        timesheetstatus=weeklytimesheetvalues[0][12]

    percent=0
    for weekly in weeklytimesheetvalues:
        percent=percent+weekly[15]
    percent=(percent/56)*100
    percent = round(percent, 2)
    context={
        "request":request,
        "current_user":current_user,
        "roleadmin" : roleadmin.value,
        "image_path_admin":image_path_adminsession.value,
        "fullname_admin" : fullname_adminsession.value,
        "weeks_in_year":weeks_in_year,
        "weekdates":weekdates,
        "year":year,
        "weeknum":weeknum,
        "weeklytimesheetvalues":weeklytimesheetvalues,
        "iduser":iduser,
        "timesheetstatus":timesheetstatus,
        "percent":percent,
        "roleuser":roleuser.value,
                "roleuser":roleuser.value,
        "image_path": image_path_session.value,
        "fullname": fullname_session.value
    } 
    return templates.TemplateResponse("ERP/WeeklyTimesheet.html",context)

@ERP.post("/WeeklyTimesheet/{iduser}/{year}/{weeknum}",tags=['ERP'],response_class=HTMLResponse)
async def weeklytimesheet(request:Request,iduser,year,weeknum,current_user: User = Depends(get_current_user_from_token)):
    # current_datetime = datetime.now()
    # year=current_datetime.year
    form = await request.form()
    if request.method=='POST' and 'yearform' in form and  form['yearform']=='yearform':
        year=form['year']
    weeks_in_year=calendar(year)

    weekdates=[]
    for week in weeks_in_year:
        if str(week['week_number']) == str(weeknum):
            weekdates = [str(date_obj['date']) for date_obj in week['week_dates']]
            break
            
    conn=db.connection()
    cursor=conn.cursor()
    sql="""select p.projectid,pt.Name,p.projectname,c.name,t.name,w.mon,w.tue,w.wed,w.thu,w.fri,w.sat,w.sun,w.statustimesheet,w.note,w.id,w.progress
 from weeklytimesheet w join project p on w.projectid=p.projectid join
 projecttype pt on pt.projecttypeid=p.projecttypeid join componentproject c on w.componentid =c.id join 
 taskproject t on w.taskid=t.id join DATE d on d.Date=w.Date where d.Year=? and d.WeekNumber=? and w.iduser=? and w.status=1"""
    values=(year,weeknum,decode_id(iduser))
    cursor.execute(sql,values)
    weeklytimesheet_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    weeklytimesheetvalues=[(project[0],project[1],project[2],project[3],project[4],project[5],
                            project[6],project[7],project[8],project[9],project[10],project[11],
                            project[12],project[13],project[14],project[15])for project in weeklytimesheet_temp]
    #listweeklytimesheetid=[(project[14])for project in weeklytimesheet_temp]
    selecttiontasks=[]
    timesheetstatus=None
    if weeklytimesheetvalues !=[]:
        timesheetstatus=weeklytimesheetvalues[0][12]

    percent=0
    for weekly in weeklytimesheetvalues:
        percent=percent+weekly[15]
    percent=(percent/56)*100
    percent = round(percent, 2)

    if request.method=='POST' and  'yearform' in form and form['yearform']=='yearform':
        year=form['year']
        weeknum=1
        return RedirectResponse(url=f"/WeeklyTimesheet/{iduser}/{year}/{weeknum}",status_code=status.HTTP_302_FOUND)

    if request.method=="POST" and  'removetasks' in form and form['removetasks']=='removetasks':
        selecttiontasks=form.getlist('checkbox')
        
        for select in selecttiontasks:
            removetasks(select)
        message=[('success','remove task is successfully')]

        return RedirectResponse(url=f"/WeeklyTimesheet/{iduser}/{year}/{weeknum}",status_code=status.HTTP_302_FOUND)
    elif request.method=="POST" and'addtasks' in form and form['addtasks']=='addtasks':
        return RedirectResponse(url=f"/WeeklyTimesheet_addtask/{iduser}/{year}/{weeknum}/{weekdates}",status_code=status.HTTP_302_FOUND)
    elif request.method=="POST" and 'savetasks' in form and form['savetasks']=='savetasks':
        listweeklytimesheet=[]
        for project in weeklytimesheet_temp:
            listweeklytimesheet.append((project[14],form.get('mon'+str(project[14])),form.get('tue'+str(project[14]))
                                        ,form.get('wed'+str(project[14])),form.get('thu'+str(project[14]))
                                        ,form.get('fri'+str(project[14])),form.get('sat'+str(project[14])),
                                        form.get('sun'+str(project[14]))))
        savetasks(listweeklytimesheet)
        message=[('success','update progress is sucessfull')]
        return RedirectResponse(url=f"/WeeklyTimesheet/{iduser}/{year}/{weeknum}",status_code=status.HTTP_302_FOUND)

    elif request.method=="POST" and 'resetvaluetasks' in form and form.get('resetvaluetasks')=='resetvaluetasks':
        selecttiontasks=form.getlist('checkbox')
        
        for select in selecttiontasks:
            resetValueTask(select)
        
        message=[('success','reset value is successfull')]
        return RedirectResponse(url=f"/WeeklyTimesheet/{iduser}/{year}/{weeknum}",status_code=status.HTTP_302_FOUND)
        
    elif request.method=="POST" and 'recalltasks'in form and form.get('recalltasks')=='recalltasks':
        #selecttiontasks=form.getlist('checkbox')
        listrecall=[]
        for project in weeklytimesheet_temp:
            listrecall.append(project[14])
        for list in listrecall:
            recalltasks(list)
        
        message=[('success','submit tasks is successfull')]
        return RedirectResponse(url=f"/WeeklyTimesheet/{iduser}/{year}/{weeknum}",status_code=status.HTTP_302_FOUND)
    elif request.method=="POST" and 'submittasks'in form and form.get('submittasks')=='submittasks':
        #selecttiontasks=form.getlist('checkbox')
        listsubmit=[]
        for project in weeklytimesheet_temp:
            listsubmit.append(project[14])
        for list in listsubmit:
            submittasks(list)
        for select in selecttiontasks:
            submittasks(select)
       
        message=[('success','submit tasks is successfull')]
        return RedirectResponse(url=f"/WeeklyTimesheet/{iduser}/{year}/{weeknum}",status_code=status.HTTP_302_FOUND)
    
    elif request.method=="POST" and 'copytasks' in form and form.get('copytasks')=='copytasks':
        copytasks()
        
        message=[('success','copy tasks is successfull')]
        return RedirectResponse(url=f"/WeeklyTimesheet/{iduser}/{year}/{weeknum}",status_code=status.HTTP_302_FOUND)
    context={
        "request":request,
        "current_user":current_user,
        "roleadmin" : roleadmin.value,
        "image_path_admin":image_path_adminsession.value,
        "fullname_admin" : fullname_adminsession.value,
        "weeks_in_year":weeks_in_year,
        "weekdates":weekdates,
        "year":year,
        "weeknum":weeknum,
        "weeklytimesheetvalues":weeklytimesheetvalues,
        "iduser":iduser,
        "timesheetstatus":timesheetstatus,
        "percent":percent,
        "roleuser":roleuser.value,
                "roleuser":roleuser.value,
        "image_path": image_path_session.value,
        "fullname": fullname_session.value
    } 
    return templates.TemplateResponse("ERP/WeeklyTimesheet.html",context)

def copytasks():
    conn=db.connection()
    cursor=conn.cursor()
    sql="""insert into weeklytimesheet(projectid,componentid,taskid,statustimesheet,note,Date,status,iduser,mon,tue,wed,thu,fri,sat,sun,progress)
        select w.projectid,w.componentid,w.taskid,w.statustimesheet,w.note,CONVERT(date, getdate()) as Date,w.status,w.iduser,w.mon,w.tue,w.wed,
        w.thu,w.fri,w.sat,w.sun,w.progress from weeklytimesheet w join DATE d on w.Date=d.Date where d.WeekNumber=(select WeekNumber from DATE where DATE=CONVERT(date, DATEADD(day, -7, GETDATE()))
        ) and w.statustimesheet!='pending approval' and w.statustimesheet!='copied'

        update weeklytimesheet set statustimesheet='copied' from weeklytimesheet w join DATE d on w.Date=d.Date where
        d.WeekNumber=(select WeekNumber from DATE where DATE=CONVERT(date, DATEADD(day, -7, GETDATE()))) and w.statustimesheet!='pending approval'
        """
    cursor.execute(sql)
    conn.commit()
    conn.close()    

def submittasks(select):
    conn=db.connection()
    cursor=conn.cursor()
    sql="update weeklytimesheet set statustimesheet='pending approval' where id=? and statustimesheet !='pending approval' and statustimesheet!='initialization'"
    cursor.execute(sql,select)
    conn.commit()
    conn.close()

def recalltasks(select):
    conn=db.connection()
    cursor=conn.cursor()
    sql="update weeklytimesheet set statustimesheet='recalling' where id=? and statustimesheet !='saved'"
    cursor.execute(sql,select)
    conn.commit()
    conn.close()

def resetValueTask(select):
    conn=db.connection()
    cursor=conn.cursor()
    sql="update weeklytimesheet set mon=0,tue=0,wed=0,thu=0, fri=0,sat=0,sun=0,progress=0 where id=? and statustimesheet !='pending approval'"
    value=(select)
    cursor.execute(sql,value)
    conn.commit()
    conn.close()

def savetasks(listweeklytimesheet):
    for weeklytimesheet in listweeklytimesheet:
        conn=db.connection()
        cursor=conn.cursor()
        sql="""update weeklytimesheet set mon=?,tue=?,wed=?,thu=?, fri=?,sat=?,sun=?,statustimesheet='saved' where id=? and statustimesheet !='pending approval'
        update weeklytimesheet set progress=(mon+tue+wed+thu+fri+sat+sun) where id=? and statustimesheet !='pending approval'"""
        value=(weeklytimesheet[1],weeklytimesheet[2],weeklytimesheet[3],weeklytimesheet[4],weeklytimesheet[5],weeklytimesheet[6],weeklytimesheet[7],weeklytimesheet[0],weeklytimesheet[0])
        cursor.execute(sql,value)
        conn.commit()
        conn.close()


def removetasks(weeklytimesheetid):
    conn=db.connection()
    cursor=conn.cursor()
    sql="delete weeklytimesheet where id=?"
    cursor.execute(sql,weeklytimesheetid)
    conn.commit()
    conn.close()

@ERP.get("/WeeklyTimesheet_addtask/{iduser}/{year}/{weeknum}/{weekdates}",tags=['ERP'],status_code=status.HTTP_302_FOUND)
async def addtask_get(request:Request,iduser,year,weeknum,weekdates,current_user: User = Depends(get_current_user_from_token)): 
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
    context={
        "request":request,
        "current_user":current_user,
        "roleadmin" : _roleadmin,
        "image_path_admin":image_path_adminsession.value,
        "fullname_admin" : fullname_adminsession.value,
        "projects":projects,
        "tasks":tasks,
        "components":components,
                "roleuser":roleuser.value,
        "image_path": image_path_session.value,
        "fullname": fullname_session.value
    }
    return templates.TemplateResponse("ERP/addtaskweeklytimesheet.html",context)     
    
@ERP.post("/WeeklyTimesheet_addtask/{iduser}/{year}/{weeknum}/{weekdates}",tags=['ERP'],status_code=status.HTTP_302_FOUND)
async def addtask(request:Request,iduser,year,weeknum,weekdates,current_user: User = Depends(get_current_user_from_token)): 
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
        current_date = datetime.now().strftime("%Y-%m-%d") 
        if current_date in weekdates:
            conn=db.connection()
            cursor=conn.cursor()
            sql="insert into weeklytimesheet(projectid,componentid,taskid,statustimesheet,Date,iduser) values(?,?,?,'initialization',CONVERT(date, GETDATE()),?)"
            value=(form_method['project'],form_method['component'],form_method['task'],decode_id(iduser))
            cursor.execute(sql,value)
            conn.commit()
            conn.close()
        else:
            conn=db.connection()
            cursor=conn.cursor()
            sql="insert into weeklytimesheet(projectid,componentid,taskid,statustimesheet,Date,iduser) values(?,?,?,'initialization',?,?)"
            value=(form_method['project'],form_method['component'],form_method['task'],str(weekdates[2:12]),decode_id(iduser))
            cursor.execute(sql,value)
            conn.commit()
            conn.close()
        messages=[('success','add task weekly timesheet is successfull')]
        return RedirectResponse(url=f"/WeeklyTimesheet/{iduser}/{year}/{weeknum}",status_code=status.HTTP_302_FOUND)
    context={
        "request":request,
        "current_user":current_user,
        "roleadmin" : _roleadmin,
        "image_path_admin":image_path_adminsession.value,
        "fullname_admin" : fullname_adminsession.value,
        "projects":projects,
        "tasks":tasks,
        "components":components,
                "roleuser":roleuser.value,
        "image_path": image_path_session.value,
        "fullname": fullname_session.value
    }
    return templates.TemplateResponse("ERP/addtaskweeklytimesheet.html",context)     
    
@ERP.post('/get_tasks_and_components',tags=['ERP'])
async def get_tasks_and_components(request:Request):
    form=await request.form()
    selected_project = form['selected_project']
    conn=db.connection()
    cursor=conn.cursor()
    sql="select t.id,t.name from taskproject t join project p on t.projectid=p.projectid where t.projectid=? and p.status=1"
    value=(selected_project)
    cursor.execute(sql,value)
    tasks_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    tasks_options = [(task[0],task[1])for task in tasks_temp]
    
    conn=db.connection()
    cursor=conn.cursor()
    sql="select c.id,c.name from componentproject c join project p on c.projectid=p.projectid where c.projectid=? and p.status=1"
    value=(selected_project)
    cursor.execute(sql,value)
    components_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    components_options =[(component[0],component[1])for component in components_temp]
    return JSONResponse(content={'tasks':tasks_options,'components':components_options})

@ERP.post("/ERP/weeklytimesheetview",response_class=HTMLResponse)
async def weeklytimesheetview(request:Request,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select projectid,projectname from project where status=1"
    cursor.execute(sql)
    projects_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    projects=[(project[0],project[1])for project in projects_temp]

    conn=db.connection()
    cursor=conn.cursor()
    sql="""select p.projectid,pt.Name,p.projectname,c.name,t.name,w.mon,w.tue,w.wed,w.thu,w.fri,w.sat,w.sun,w.statustimesheet,w.note,w.id,w.progress,w.Date
 from weeklytimesheet w join project p on w.projectid=p.projectid join
 projecttype pt on pt.projecttypeid=p.projecttypeid join componentproject c on w.componentid =c.id join 
 taskproject t on w.taskid=t.id join DATE d on d.Date=w.Date where w.statustimesheet ='pending approval' """
    cursor.execute(sql)
    weeklytimesheet=cursor.fetchall()
    conn.commit()
    conn.close()
    weeklytimesheetvalues=[(project[0],project[1],project[2],project[3],project[4],project[5],
                            project[6],project[7],project[8],project[9],project[10],project[11],
                            project[12],project[13],project[14],project[15],project[16])for project in weeklytimesheet]
    form_method=await request.form()
    if  form_method.get('searchproject')=='searchproject':
        
        conn=db.connection()
        cursor=conn.cursor()
        sql="""select p.projectid,pt.Name,p.projectname,c.name,t.name,w.mon,w.tue,w.wed,w.thu,w.fri,w.sat,w.sun,w.statustimesheet,w.note,w.id,w.progress,w.Date
    from weeklytimesheet w join project p on w.projectid=p.projectid join
    projecttype pt on pt.projecttypeid=p.projecttypeid join componentproject c on w.componentid =c.id join 
    taskproject t on w.taskid=t.id join DATE d on d.Date=w.Date where w.statustimesheet ='pending approval' and w.projectid=? """
        cursor.execute(sql,form_method['project'])
        weeklytimesheet=cursor.fetchall()
        conn.commit()
        conn.close()
        weeklytimesheetvalues=[(project[0],project[1],project[2],project[3],project[4],project[5],
                                project[6],project[7],project[8],project[9],project[10],project[11],
                                project[12],project[13],project[14],project[15],project[16])for project in weeklytimesheet]

    context={
        "request":request,
        "current_user":current_user,
        "roleadmin" : _roleadmin,
        "image_path_admin":image_path_adminsession.value,
        "fullname_admin" : fullname_adminsession.value,
        "projects":projects,
        "weeklytimesheetvalues":weeklytimesheetvalues,
        "projects":projects
    }
    return templates.TemplateResponse("ERP/weeklytimesheetviewadmin.html",context)
    

@ERP.get("/ERP/weeklytimesheetview",response_class=HTMLResponse)
async def weeklytimesheetview_get(request:Request,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select projectid,projectname from project where status=1"
    cursor.execute(sql)
    projects_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    projects=[(project[0],project[1])for project in projects_temp]

    conn=db.connection()
    cursor=conn.cursor()
    sql="""select p.projectid,pt.Name,p.projectname,c.name,t.name,w.mon,w.tue,w.wed,w.thu,w.fri,w.sat,w.sun,w.statustimesheet,w.note,w.id,w.progress,w.Date
 from weeklytimesheet w join project p on w.projectid=p.projectid join
 projecttype pt on pt.projecttypeid=p.projecttypeid join componentproject c on w.componentid =c.id join 
 taskproject t on w.taskid=t.id join DATE d on d.Date=w.Date where w.statustimesheet ='pending approval' """
    cursor.execute(sql)
    weeklytimesheet=cursor.fetchall()
    conn.commit()
    conn.close()
    weeklytimesheetvalues=[(project[0],project[1],project[2],project[3],project[4],project[5],
                            project[6],project[7],project[8],project[9],project[10],project[11],
                            project[12],project[13],project[14],project[15],project[16])for project in weeklytimesheet]
    
    context={
        "request":request,
        "current_user":current_user,
        "roleadmin" : _roleadmin,
        "image_path_admin":image_path_adminsession.value,
        "fullname_admin" : fullname_adminsession.value,
        "projects":projects,
        "weeklytimesheetvalues":weeklytimesheetvalues,
        "projects":projects
    }
    return templates.TemplateResponse("ERP/weeklytimesheetviewadmin.html",context)
    