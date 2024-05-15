import db
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from authentication.models import get_current_user_from_cookie,get_current_user_from_token
from authentication.models import User
from ultils import file_path_default,encode_id,decode_id
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
import ast
templates = Jinja2Templates(directory="templates")
payroll = APIRouter()

def count_weekdays(start_date, end_date):
    current_date = start_date
    weekdays_count = 0
    
    while current_date <= end_date:
        # Kiểm tra nếu ngày hiện tại không phải là Thứ Bảy hoặc Chủ Nhật (0 là Chủ Nhật, 6 là Thứ Bảy)
        if current_date.weekday() != 5 and current_date.weekday() != 6:
            weekdays_count += 1
        current_date += timedelta(days=1)
    
    return weekdays_count


def tinhluongnhanvientra(g,grosssalary):
    #nhan vien
    bhxh=1800000*20*0.08
    bhyt=1800000*20*0.015
    bhtn=0
    bhtnct=0
    if g[1]=='1':
        bhtn=4680000*20*0.01
        bhtnct=4680000*20*0.01
    elif g[1]=='2':
        bhtn=4160000*20*0.01
        bhtnct=4160000*20*0.01
    elif g[1]=='3':
        bhtn=3640000*20*0.01
        bhtnct=3640000*20*0.01
    elif g[1]=='4':
        bhtn=3250000*20*0.01
        bhtnct=3250000*20*0.01
    giacanhbanthan=11000000
    giacanhnguoiphuthuoc=4400000*int(g[7])
    thunhaptruocthue=grosssalary-bhxh-bhyt-bhtn
    thunhapchiuthue=thunhaptruocthue-giacanhbanthan-giacanhnguoiphuthuoc
    thuethunhap=0
    if int(thunhapchiuthue<=5000000):
        thuethunhap=thunhapchiuthue*0.05
    elif int(thunhapchiuthue>5000000 and thunhapchiuthue<=10000000 ):
        thuethunhap=thunhapchiuthue*0.1
    elif int(thunhapchiuthue>10000000 and thunhapchiuthue<=18000000 ):
        thuethunhap=thunhapchiuthue*0.15
    elif int(thunhapchiuthue>18000000 and thunhapchiuthue<=32000000 ):
        thuethunhap=thunhapchiuthue*0.2   
    elif int(thunhapchiuthue>32000000 and thunhapchiuthue<=52000000 ):
        thuethunhap=thunhapchiuthue*0.25
    elif int(thunhapchiuthue>52000000 and thunhapchiuthue<=80000000 ):
        thuethunhap=thunhapchiuthue*0.30
    elif int(thunhapchiuthue>80000000):
        thuethunhap=thunhapchiuthue*0.35
    netsalary=thunhaptruocthue-thuethunhap
    #congty
    bhxhct=1800000*20*0.17
    bhtnldct=1800000*20*0.005
    bhytct=1800000*20*0.03
    tongcongcongtytra=grosssalary+bhxhct+bhtnct+bhytct+bhtnldct
    sumsalary=[grosssalary,bhxh,bhyt,bhtn,giacanhbanthan,giacanhnguoiphuthuoc
               ,thunhaptruocthue,thunhapchiuthue,thuethunhap,netsalary,
               bhxhct,bhtnldct,bhytct,bhtnct,tongcongcongtytra]
    return sumsalary


def dayoffinmonth(id,last_month_25_str,current_month_25_str):
    last_month_25=datetime.strptime(last_month_25_str, '%Y-%m-%d').date()
    current_month_25=datetime.strptime(current_month_25_str, '%Y-%m-%d').date()
    conn=db.connection()
    cursor=conn.cursor()
    sql="""
    select p.projectid,pt.Name,p.projectname,c.name,t.name,w.mon,w.tue,w.wed,w.thu,w.fri,w.sat,w.sun,w.statustimesheet,w.note,w.id,w.progress,w.Date,d.WeekNumber,w.iduser
 from weeklytimesheet w join project p on w.projectid=p.projectid join
 projecttype pt on pt.projecttypeid=p.projecttypeid join componentproject c on w.componentid =c.id join 
 taskproject t on w.taskid=t.id join DATE d on d.Date=w.Date where d.Year=2024 and 
 d.date BETWEEN ? AND ? and w.iduser=? and w.status=1 and w.statustimesheet='approval' and pt.Name='Non-Project'
 """
    value=(last_month_25_str,current_month_25_str,id)
    cursor.execute(sql,value)
    temp=cursor.fetchall()
    conn.commit()
    conn.close()
    dayoff=0
    for d in temp:
        start_of_week = d[16] - timedelta(days=d[16].weekday())
        array=[]
        # In ra các ngày từ thứ 2 đến thứ 7
        for i in range(1, 8):
            day = start_of_week + timedelta(days=i)
            day=datetime.strptime(day.strftime('%Y-%m-%d'), '%Y-%m-%d').date()
            
            if last_month_25<= day<=current_month_25:
                if i==1:
                    dayoff=dayoff + int(d[5])
                elif i==2:
                    dayoff=dayoff + int(d[6])
                elif i==3:
                    dayoff=dayoff + int(d[7])
                elif i==4:
                    dayoff=dayoff + int(d[8])
                elif i==5:
                    dayoff=dayoff + int(d[9])
                elif i==6:
                    dayoff=dayoff + int(d[10])
                elif i==7:
                    dayoff=dayoff + int(d[11])
    dayoff=dayoff/8
    return dayoff
       


@payroll.get("/payroll",tags=['payroll'], response_class=HTMLResponse)
async def payrolllist(request:Request,current_user: User = Depends(get_current_user_from_token)):
    # Lấy ngày hiện tại
    today = datetime.today()

    # Tính ngày 25 của tháng hiện tại
    current_month_25 = today.replace(day=25)

    # Tính ngày 25 của tháng trước
    last_month_25 = (current_month_25 - relativedelta(months=1)).replace(day=25)

    # Định dạng ngày theo '%Y-%m-%d'
    current_month_25_str = current_month_25.strftime('%Y-%m-%d')
    last_month_25_str = last_month_25.strftime('%Y-%m-%d')
    print(f"Từ ngày 25 tháng trước: {last_month_25_str}")
    print(f"Đến ngày 25 tháng này: {current_month_25_str}")

    conn=db.connection()
    cursor=conn.cursor()
    sql="SELECT i.id,l.dayoff FROM informationUser i join informationUserJob ij on i.id=ij.idinformationuser join laborContract l on l.idinformationUserJob=ij.id"
    cursor.execute(sql)
    idtemp=cursor.fetchall()
    conn.commit()
    conn.close()
    dayofflist=[]
    for id in idtemp:
        dayoff=dayoffinmonth(id[0],last_month_25_str,current_month_25_str)
        id_dayoff=[id[0],dayoff,id[1]]
        dayofflist.append(id_dayoff)

    conn=db.connection()
    cursor=conn.cursor()
    sql="""
    SELECT i.id, i.companysitecode, l.dayoff, f.Annualsalary, f.Monthlysalaryincontract, f.Quaterlybonustarget, f.Annualbonustarget, 
    COALESCE(SUM(CASE WHEN ei.col_Dependant = 1 THEN 1 ELSE 0 END), 0) AS TotalDependants,inf.Email,inf.id
FROM informationUserJob i 
JOIN laborContract l ON i.id = l.idinformationUserJob 
JOIN forexSalary f ON f.idinformationUserJob = i.id 
JOIN informationUser inf ON inf.id = i.idinformationuser 
LEFT JOIN employeerelative_informationuser ei ON ei.idinformationuser = inf.id
where i.is_active=1 and l.is_active=1 and f.is_active=1
GROUP BY i.id, i.companysitecode, l.dayoff, f.Annualsalary, f.Monthlysalaryincontract, f.Quaterlybonustarget, f.Annualbonustarget,inf.Email,inf.id"""
    cursor.execute(sql)
    grosstemp=cursor.fetchall()
    conn.commit()
    conn.close()
    gross=[(p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8],p[9])for p in grosstemp]

    tempsumsalary=[]
    for g in gross:
        for d in dayofflist:
            if d[0]==g[9]:
                grosssalary=int(g[3])+int(g[4])+int(g[5])+int(g[6])
                if int(d[1])>int(d[2]):
                    a=int(d[1])-int(d[2])
                    weekdays_count= count_weekdays(last_month_25,current_month_25)
                    percentworkinmonth=(weekdays_count-a)/weekdays_count
                    salaryincontract=int(g[4])*percentworkinmonth
                    grosssalary=salaryincontract
                salary=tinhluongnhanvientra(g,grosssalary)
                salary.append(g[8])
                salary.append(d[1])
                salary.append(g[9])
                salary.append(str(g[7]))
        tempsumsalary.append(salary)
    context={
        "request":request,
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleuser":request.cookies.get("roleuser"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession"),
        "current_user":current_user,
        "tempsumsalary":tempsumsalary
    }
    return templates.TemplateResponse("payroll/payrolllist.html",context)

    

@payroll.get("/payrolldetail/{iduser}/{tempsumsalary}",tags=['payroll'], response_class=HTMLResponse)
async def payrolldetail(request:Request,iduser,tempsumsalary,current_user: User = Depends(get_current_user_from_token)):
    data_list = ast.literal_eval(tempsumsalary)
    detail=[]
    totalinsurance=0
    for d in data_list:
        if str(d[17])==iduser:
            totalinsurance=int(d[1])+int(d[2])+int(d[3])
            
            detail=d
            break
    context={
        "request":request,
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleuser":request.cookies.get("roleuser"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession"),
        "current_user":current_user,
        "detail":detail,
        "totalinsurance":str(totalinsurance)
    }
    return templates.TemplateResponse("payroll/payrollDetail.html",context)