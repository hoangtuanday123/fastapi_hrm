import db
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse,FileResponse,StreamingResponse
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from authentication.models import get_current_user_from_cookie,get_current_user_from_token
from authentication.models import User
from ultils import file_path_default,encode_id,decode_id
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
import ast
import uuid
import pandas as pd
from io import BytesIO
import pdfkit
import zipfile
import io


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

def calculate_pit(taxable_income):
    if taxable_income <= 0:
        return 0

    brackets = [
        (0,5000000, 0.05),
        (5000000,10000000, 0.1),
        (10000000,18000000, 0.15),
        (18000000,32000000, 0.2),
        (32000000,52000000, 0.25),
        (52000000,80000000, 0.3),
        (80000000,float('inf'), 0.35)
    ]

    # Calculate tax
    tax = 0
    for bracket_under_limit,bracket_top_limit, rate in brackets:
        if taxable_income > bracket_top_limit:
            tax += (bracket_top_limit-bracket_under_limit) * rate
            if bracket_under_limit == "80000000":
                tax += (taxable_income-bracket_under_limit) * rate
                break
        else:
            tax += (taxable_income-bracket_under_limit) * rate
            break

    return tax

def tinhluongnhanvientra(g,grosssalary):
    #nhan vien
    bhxh=1800000*20*0.08
    bhyt=1800000*20*0.015
    bhtn=0
    bhtnct=0
    if g[1]=='1':
        bhtn=4680000*20*0.01*1.07
        bhtnct=4680000*20*0.01*1.07
    elif g[1]=='2':
        bhtn=4160000*20*0.01*1.07
        bhtnct=4160000*20*0.01*1.07
    elif g[1]=='3':
        bhtn=3640000*20*0.01*1.07
        bhtnct=3640000*20*0.01*1.07
    elif g[1]=='4':
        bhtn=3250000*20*0.01*1.07
        bhtnct=3250000*20*0.01*1.07
    giacanhbanthan=11000000
    giacanhnguoiphuthuoc=4400000*int(g[7])
    thunhaptruocthue=grosssalary-bhxh-bhyt-bhtn
    thunhapchiuthue=thunhaptruocthue-giacanhbanthan-giacanhnguoiphuthuoc
    thuethunhap=calculate_pit(thunhapchiuthue)
    # if int(thunhapchiuthue<=5000000):
    #     thuethunhap=thunhapchiuthue*0.05
    # elif int(thunhapchiuthue>5000000 and thunhapchiuthue<=10000000 ):
    #     thuethunhap=thunhapchiuthue*0.1
    # elif int(thunhapchiuthue>10000000 and thunhapchiuthue<=18000000 ):
    #     thuethunhap=thunhapchiuthue*0.15
    # elif int(thunhapchiuthue>18000000 and thunhapchiuthue<=32000000 ):
    #     thuethunhap=thunhapchiuthue*0.2   
    # elif int(thunhapchiuthue>32000000 and thunhapchiuthue<=52000000 ):
    #     thuethunhap=thunhapchiuthue*0.25
    # elif int(thunhapchiuthue>52000000 and thunhapchiuthue<=80000000 ):
    #     thuethunhap=thunhapchiuthue*0.30
    # elif int(thunhapchiuthue>80000000):
    #     thuethunhap=thunhapchiuthue*0.35
    netsalary=thunhaptruocthue-thuethunhap
    #congty
    bhxhct=1800000*20*0.17
    bhtnldct=1800000*20*0.005
    bhytct=1800000*20*0.03
    tongcongcongtytra=grosssalary+bhxhct+bhtnct+bhytct+bhtnldct
    sumsalary=[round(grosssalary),bhxh,bhyt,bhtn,giacanhbanthan,giacanhnguoiphuthuoc
               ,round(thunhaptruocthue),round(thunhapchiuthue),round(thuethunhap),round(netsalary),
               bhxhct,bhtnldct,bhytct,bhtnct,round(tongcongcongtytra)]
    return sumsalary




def dayoffinmonth(id,last_month_25_str,current_month_25_str):
    last_month_25=datetime.strptime(last_month_25_str, '%Y-%m-%d').date()
    current_month_25=datetime.strptime(current_month_25_str, '%Y-%m-%d').date()
    current_date = last_month_25
    listdate_30=[]
    while current_date<=current_month_25:
        listdate_30.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    conn=db.connection()
    cursor=conn.cursor()
#     sql="""
#      select p.projectid,pt.Name,p.projectname,c.name,t.name,w.mon,w.tue,w.wed,w.thu,w.fri,w.sat,w.sun,w.statustimesheet,w.note,w.id,w.progress,w.Date,d.WeekNumber,w.iduser
#  from weeklytimesheet w join project p on w.projectid=p.projectid join
#  projecttype pt on pt.projecttypeid=p.projecttypeid LEFT JOIN componentproject c on w.componentid =c.id join 
#  taskproject t on w.taskid=t.id join DATE d on d.Date=w.Date where d.Year=2024 and 
#  d.date BETWEEN ? AND ? and w.iduser=? and w.status=1 and w.statustimesheet='approval' and pt.Name='Non-Project' and t.name='unpaid days off'
#  """
#     value=(last_month_25_str,current_month_25_str,id)
    sql="""
    select d.* from dayofftimesheet d join date da on d.startdate=da.Date join date da1 on da1.Date=d.enddate 
where d.iduser=? and d.startdate BETWEEN ? AND ? or d.iduser=? and d.enddate BETWEEN ? AND ?
"""
    values=(id,last_month_25,current_month_25,id,last_month_25,current_month_25)
    cursor.execute(sql,values)
    temp=cursor.fetchall()
    conn.commit()
    conn.close()
    dayoff=0
    listdate=[]
    for d in temp:
        startdate=datetime.strptime(str(d[5]), '%Y-%m-%d').date()
        enddate=datetime.strptime(str(d[6]), '%Y-%m-%d').date()
        current_date = startdate
        while current_date<=enddate:
            listdate.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        for date in listdate:
            if date in listdate_30:
                dayoff=dayoff+1
        listdate.clear()
    return dayoff
        
    
       
@payroll.get("/payrollmanagement",tags=['payroll'], response_class=HTMLResponse)
async def payrollmanagement(request:Request,current_user: User = Depends(get_current_user_from_token)):
    current_date = datetime.now()

    # Lấy tháng và năm hiện tại
    current_month = current_date.month
    current_year = current_date.year
    return RedirectResponse(url=f"/payroll/{current_month}/{current_year}",status_code=status.HTTP_302_FOUND)


@payroll.get("/payrollmanagementemployee",tags=['payroll'], response_class=HTMLResponse)
async def payrollmanagementemployee(request:Request,current_user: User = Depends(get_current_user_from_token)):
    current_date = datetime.now()

    # Lấy tháng và năm hiện tại
    current_month = current_date.month
    current_year = current_date.year
    return RedirectResponse(url=f"/payrollemployee/{current_month}/{current_year}",status_code=status.HTTP_302_FOUND)

@payroll.get("/payroll/{month}/{year}",tags=['payroll'], response_class=HTMLResponse)
async def payrolllist_get(request:Request,month,year,current_user: User = Depends(get_current_user_from_token)):
    current_month_25_str=None
    last_month_25_str=None
    current_date = datetime.now()

    # Lấy tháng và năm hiện tại
    current_month = current_date.month
    current_year = current_date.year
    if month==str(current_month) and year==str(current_year):
        # Lấy ngày hiện tại
        today = datetime.today()

        # Tính ngày 25 của tháng hiện tại
        current_month_25 = today.replace(day=25)

        # Tính ngày 25 của tháng trước
        last_month_25 = (current_month_25 - relativedelta(months=1)).replace(day=25)

        # Định dạng ngày theo '%Y-%m-%d'
        current_month_25_str = current_month_25.strftime('%Y-%m-%d')
        last_month_25_str = last_month_25.strftime('%Y-%m-%d')
    else:
        current_month_25 = datetime(year=int(year), month=int(month), day=25)

        # Tính ngày 25 của tháng trước
        last_month_25 = (current_month_25 - relativedelta(months=1)).replace(day=25)
        current_month_25_str = current_month_25.strftime('%Y-%m-%d')
        last_month_25_str = last_month_25.strftime('%Y-%m-%d')


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
    COALESCE(SUM(CASE WHEN ei.col_Dependant = 1 THEN 1 ELSE 0 END), 0) AS TotalDependants,inf.Email,inf.id, inf.Fullname
FROM informationUserJob i 
JOIN laborContract l ON i.id = l.idinformationUserJob 
JOIN forexSalary f ON f.idinformationUserJob = i.id 
JOIN informationUser inf ON inf.id = i.idinformationuser 
LEFT JOIN employeerelative_informationuser ei ON ei.idinformationuser = inf.id
where i.is_active=1 and l.is_active=1 and f.is_active=1
GROUP BY i.id, i.companysitecode, l.dayoff, f.Annualsalary, f.Monthlysalaryincontract, f.Quaterlybonustarget, f.Annualbonustarget,inf.Email,inf.id,inf.Fullname"""
    cursor.execute(sql)
    grosstemp=cursor.fetchall()
    conn.commit()
    conn.close()
    gross=[(p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8],p[9],p[10])for p in grosstemp]

    tempsumsalary=[]
    for g in gross:
        for d in dayofflist:
            if d[0]==g[9]:
                
                weekdays_count= count_weekdays(last_month_25,current_month_25)
                offset=int(d[1])
                actualday=weekdays_count-offset
                percentworkinmonth=actualday/weekdays_count
                amoundgrosssalary=round(int(g[4])*percentworkinmonth)
                totalincome=int(g[3])+amoundgrosssalary+int(g[5])+int(g[6])
                salary=tinhluongnhanvientra(g,totalincome)
                salary.append(g[8])
                salary.append(round(d[1]))
                salary.append(round(g[9]))
                salary.append(str(g[7]))
                salary.append(str(weekdays_count))
                salary.append(str(offset))
                salary.append(str(actualday))
                salary.append(str(round(g[4])))
                salary.append(g[10]),
                salary.append(amoundgrosssalary)
        tempsumsalary.append(salary)
    context={
        "request":request,
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleuser":request.cookies.get("roleuser"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession"),
        "current_user":current_user,
        "tempsumsalary":tempsumsalary,
        "current_month":str(current_month),
        "current_year":str(current_year),
        "year":year,
        "month":month
    }
    return templates.TemplateResponse("payroll/payrolllist.html",context)

@payroll.post("/payroll/{month}/{year}",tags=['payroll'], response_class=HTMLResponse)
async def payrolllist(request:Request,month,year,current_user: User = Depends(get_current_user_from_token)):
    current_month_25_str=None
    last_month_25_str=None
    current_date = datetime.now()

    # Lấy tháng và năm hiện tại
    current_month = current_date.month
    current_year = current_date.year
    if month==str(current_month) and year==str(current_year):
        # Lấy ngày hiện tại
        today = datetime.today()

        # Tính ngày 25 của tháng hiện tại
        current_month_25 = today.replace(day=25)

        # Tính ngày 25 của tháng trước
        last_month_25 = (current_month_25 - relativedelta(months=1)).replace(day=25)

        # Định dạng ngày theo '%Y-%m-%d'
        current_month_25_str = current_month_25.strftime('%Y-%m-%d')
        last_month_25_str = last_month_25.strftime('%Y-%m-%d')
    else:
        current_month_25 = datetime(year=int(year), month=int(month), day=25)

        # Tính ngày 25 của tháng trước
        last_month_25 = (current_month_25 - relativedelta(months=1)).replace(day=25)
        current_month_25_str = current_month_25.strftime('%Y-%m-%d')
        last_month_25_str = last_month_25.strftime('%Y-%m-%d')


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
    COALESCE(SUM(CASE WHEN ei.col_Dependant = 1 THEN 1 ELSE 0 END), 0) AS TotalDependants,inf.Email,inf.id, inf.Fullname
FROM informationUserJob i 
JOIN laborContract l ON i.id = l.idinformationUserJob 
JOIN forexSalary f ON f.idinformationUserJob = i.id 
JOIN informationUser inf ON inf.id = i.idinformationuser 
LEFT JOIN employeerelative_informationuser ei ON ei.idinformationuser = inf.id
where i.is_active=1 and l.is_active=1 and f.is_active=1
GROUP BY i.id, i.companysitecode, l.dayoff, f.Annualsalary, f.Monthlysalaryincontract, f.Quaterlybonustarget, f.Annualbonustarget,inf.Email,inf.id,inf.Fullname"""
    cursor.execute(sql)
    grosstemp=cursor.fetchall()
    conn.commit()
    conn.close()
    gross=[(p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8],p[9],p[10])for p in grosstemp]

    tempsumsalary=[]
    for g in gross:
        for d in dayofflist:
            if d[0]==g[9]:
                weekdays_count= count_weekdays(last_month_25,current_month_25)
                offset=int(d[1])
                actualday=weekdays_count-offset
                percentworkinmonth=actualday/weekdays_count
                amoundgrosssalary=int(g[4])*percentworkinmonth
                totalincome=int(g[3])+amoundgrosssalary+int(g[5])+int(g[6])
                salary=tinhluongnhanvientra(g,totalincome)
                salary.append(g[8])
                salary.append(round(d[1]))
                salary.append(round(g[9]))
                salary.append(str(g[7]))
                salary.append(str(weekdays_count))
                salary.append(str(offset))
                salary.append(str(actualday))
                salary.append(str(round(g[4])))
                salary.append(g[10]),
                salary.append(amoundgrosssalary)
        
        tempsumsalary.append(salary)
    form_method=await request.form()
    if "savepayroll" in form_method and form_method.get("savepayroll")=="savepayroll":
       
        savepayroll(tempsumsalary,month,year)
        return RedirectResponse(url=f"/payroll/{month}/{year}",status_code=status.HTTP_302_FOUND)
    if "exportexcels" in form_method and form_method.get("exportexcels")=="exportexcels":
        iduserlist=form_method.getlist("checkbox")
        file_path=exportexcels(iduserlist,month,year)
        return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        #return str(file_path)
    if 'exportpdf' in form_method and form_method.get("exportpdf")=="exportpdf":
        iduserlist=form_method.getlist("checkbox")
        if len(iduserlist)==1:
          
            pdf_content = exportfilepdf(request,iduserlist[0],month,year)
            response = Response(pdf_content)
            filepath=f'payroll'+iduserlist[0]+'.pdf'
            response.headers["Content-Disposition"] = f"attachment; filename={filepath}"
            response.headers["Content-Type"] = "application/pdf"

            return response
        else:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                for id in iduserlist:
                    if(str(id)!='None'):
                        
                        pdf_content = exportfilepdf(request,id,month,year)
                        zip_file.writestr(f'payroll '+id+'.pdf', pdf_content)
            zip_buffer.seek(0)
            response = Response(zip_buffer.read())
            response.headers["Content-Disposition"] = "attachment; filename=your_zip_file_pdf.zip"
            response.headers["Content-Type"] = "application/zip"

            return response
        

        

    return RedirectResponse(url=f"/payroll/{form_method.get("month")}/{form_method.get("year")}",status_code=status.HTTP_302_FOUND)
    # context={
    #     "request":request,
    #     "image_path_admin":request.cookies.get("image_path_adminsession"),
    #     "roleuser":request.cookies.get("roleuser"),
    #     "roleadmin":request.cookies.get("roleadmin"),
    #     "fullname_admin":request.cookies.get("fullname_adminsession"),
    #     "current_user":current_user,
    #     "tempsumsalary":tempsumsalary,
    #     "current_month":str(current_month),
    #     "current_year":str(current_year),
    #     "year":year,
    #     "month":month
    # }
    # return templates.TemplateResponse("payroll/payrolllist.html",context)

def exportfilepdf(request:Request,iduser,month,year):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select p.*,l.Position from payroll p join informationUser i on p.iduser=i.id join informationUserJob ij on i.id=ij.idinformationuser join laborContract l on l.idinformationUserJob=ij.id where p.iduser=? and p.month=? and p.year=?"
    values=(iduser,month,year)
    cursor.execute(sql,values)
    export=cursor.fetchone()
    conn.commit()
    conn.close()
    context={
            "request":request ,
            "payrolldetail":export     
    }
    html=templates.TemplateResponse("payroll/payrollpdf.html",context).body.decode("utf-8")
    path_to_wkhtmltopdf = 'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
    pdf=pdfkit.from_string(str(html),False,configuration=config,options={"enable-local-file-access": ""})
    return pdf 



def exportexcels(iduserlist,month,year):
    datalist=[]
    priod=''
    for id in iduserlist:
        conn=db.connection()
        cursor=conn.cursor()
        sql="select p.*,l.Position from payroll p join informationUser i on p.iduser=i.id join informationUserJob ij on i.id=ij.idinformationuser join laborContract l on l.idinformationUserJob=ij.id where p.iduser=? and p.month=? and p.year=?"
        values=(id,month,year)
        cursor.execute(sql,values)
        export=cursor.fetchone()
        conn.commit()
        conn.close()
        priod=str(export[26])+"-"+str(export[27])
        data=[priod,export[1],export[3],export[28],0,export[7],0,0,0,0,export[6],export[24],0,0,0,0,0,0,export[8],export[16],
              0,export[9],0,export[16],0,0,export[18],export[19],export[21],export[22],
              export[10],export[11],export[12],export[23],0]
        datalist.append(data)
    df = pd.DataFrame(datalist, columns=['Priod', 'Emp.No MSNV', 'Full Name', 'Position','Basic salary','Monthly salary','Transportation allowance','Meal allowance','Internet Allowance','phone Allowance'
                                         ,'Working day','Amount','Transportation allowance','Meal allowance','Internet Allowance','phone Allowance','overtime'
                                              ,'Year end bonus','Total Income','Taxable income','personal','dependent','BHXH/SI','Income taxs','PIT TTNCN','Other after tax','Net Take Home',
                                              'SI BHXH(17.5%)','HI BHYT(3%)','UI BHTN(1%)','SI BHXH(8%)','HI BHYT(1.5%)','UI BHTN(1%)','Total Companys SHUI','Total EEs SHUI'])
    file_path='payroll'+priod+'.xlsx'
    df.to_excel(file_path, sheet_name='Sheet_name_1')
    #return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    return file_path
    
  

def savepayroll(salarylist,month,year):
    for salary in salarylist:
        conn=db.connection()
        cursor=conn.cursor()
        sql="select * from payroll where iduser=? and month=? and year=?"
        values=(salary[17],month,year)
        cursor.execute(sql,values)
        temp=cursor.fetchone()
        conn.commit()
        conn.close()
        if temp :
            conn=db.connection()
            cursor=conn.cursor()
            sql="""
            update payroll set offset=?, standardofworkingday=?,
            actualday=?, grosssalaryincontract=?, grosssalary=?, dependants=?, bhxh=?, 
            bhyt=?, bhtn=?, giacanhbanthan=?, giacanhnguoiphuthuoc=?, thunhaptruocthue=?, 
            thunhapchiuthue=?, thuethunhap=?, netsalary=?, bhxhct=?, bhtnldct=?, 
            bhytct=?, bhtnct=?, tongcongtytra=?,amoundgrosssalary=?, createdate=getdate() where iduser=? and month=? and year=?
            """
            values=(salary[20],salary[19],salary[21],salary[22],
                    salary[0],salary[18],salary[1],salary[2],salary[3],salary[4],salary[5],salary[6],
                    salary[7],salary[8],salary[9],salary[10],salary[11],salary[12],salary[13],salary[14],
                    salary[24],salary[17],month,year)
            cursor.execute(sql,values)
            conn.commit()
            conn.close()
        else:
            conn=db.connection()
            cursor=conn.cursor()
            sql="""
    INSERT INTO payroll(iduser, email, fullname, offset, standardofworkingday,
    actualday, grosssalaryincontract, grosssalary, dependants, bhxh, 
    bhyt, bhtn, giacanhbanthan, giacanhnguoiphuthuoc, thunhaptruocthue, 
    thunhapchiuthue, thuethunhap, netsalary, bhxhct, bhtnldct, 
    bhytct, bhtnct, tongcongtytra,amoundgrosssalary, createdate, month, year) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, GETDATE(), ?, ?)
    """
            values=(salary[17],salary[15],salary[23],salary[20],salary[19],salary[21],salary[22],
                    salary[0],salary[18],salary[1],salary[2],salary[3],salary[4],salary[5],salary[6],
                    salary[7],salary[8],salary[9],salary[10],salary[11],salary[12],salary[13],salary[14],salary[24],
                    month,year)
            cursor.execute(sql,values)
            conn.commit()
            conn.close()
        

@payroll.get("/payrolldetail/{iduser}/{month}/{year}",tags=['payroll'], response_class=HTMLResponse)
async def payrolldetail(request:Request,iduser,month,year,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from payroll where iduser=? and month=? and year=?"
    values=(iduser,month,year)
    cursor.execute(sql,values)
    payrolldetail=cursor.fetchone()
    conn.commit()
    conn.close()
    first_day_of_month = datetime(int(year), int(month), 1)
    first_day_of_month_str=first_day_of_month.strftime('%Y-%m-%d')
    last_day = calendar.monthrange(int(year), int(month))
    last_day_of_month = datetime(int(year), int(month), last_day[1])
    last_day_of_month_str=last_day_of_month.strftime('%Y-%m-%d')
    createdate= datetime(int(year), int(month), 25)
    createdate_str=createdate.strftime('%Y-%m-%d')
    context={
        "request":request,
        "image_path":request.cookies.get("image_path_session"),
        "roleuser":request.cookies.get("roleuser"),
        "fullname":request.cookies.get("fullname_session"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleuser":request.cookies.get("roleuser"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession"),
        "current_user":current_user,
        "payrolldetail":payrolldetail,
        "startdate":first_day_of_month_str,
        "enddate":last_day_of_month_str,
        "createdate":createdate_str
    }
    return templates.TemplateResponse("payroll/payrollDetail.html",context)


@payroll.get("/payrollemployee/{month}/{year}",tags=['payroll'], response_class=HTMLResponse)
async def payrolllistemployee_get(request:Request,month,year,current_user: User = Depends(get_current_user_from_token)):
    current_month_25_str=None
    last_month_25_str=None
    current_date = datetime.now()

    # Lấy tháng và năm hiện tại
    current_month = current_date.month
    current_year = current_date.year
    if month==str(current_month) and year==str(current_year):
        # Lấy ngày hiện tại
        today = datetime.today()

        # Tính ngày 25 của tháng hiện tại
        current_month_25 = today.replace(day=25)

        # Tính ngày 25 của tháng trước
        last_month_25 = (current_month_25 - relativedelta(months=1)).replace(day=25)

        # Định dạng ngày theo '%Y-%m-%d'
        current_month_25_str = current_month_25.strftime('%Y-%m-%d')
        last_month_25_str = last_month_25.strftime('%Y-%m-%d')
    else:
        current_month_25 = datetime(year=int(year), month=int(month), day=25)

        # Tính ngày 25 của tháng trước
        last_month_25 = (current_month_25 - relativedelta(months=1)).replace(day=25)
        current_month_25_str = current_month_25.strftime('%Y-%m-%d')
        last_month_25_str = last_month_25.strftime('%Y-%m-%d')

 
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from payroll where iduser=? and month=? and year=?"
    values=(decode_id(current_user.idinformationuser),month,year)
    cursor.execute(sql,values)
    payroll=cursor.fetchone()
    conn.commit()
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
        "current_month":str(current_month),
        "current_year":str(current_year),
        "year":year,
        "month":month,
        "payroll":payroll
    }
    return templates.TemplateResponse("payroll/payrolllistemployee.html",context)


@payroll.post("/payrollemployee/{month}/{year}",tags=['payroll'], response_class=HTMLResponse)
async def payrolllistemployee(request:Request,month,year,current_user: User = Depends(get_current_user_from_token)):
    current_month_25_str=None
    last_month_25_str=None
    current_date = datetime.now()

    # Lấy tháng và năm hiện tại
    current_month = current_date.month
    current_year = current_date.year
    if month==str(current_month) and year==str(current_year):
        # Lấy ngày hiện tại
        today = datetime.today()

        # Tính ngày 25 của tháng hiện tại
        current_month_25 = today.replace(day=25)

        # Tính ngày 25 của tháng trước
        last_month_25 = (current_month_25 - relativedelta(months=1)).replace(day=25)

        # Định dạng ngày theo '%Y-%m-%d'
        current_month_25_str = current_month_25.strftime('%Y-%m-%d')
        last_month_25_str = last_month_25.strftime('%Y-%m-%d')
    else:
        current_month_25 = datetime(year=int(year), month=int(month), day=25)

        # Tính ngày 25 của tháng trước
        last_month_25 = (current_month_25 - relativedelta(months=1)).replace(day=25)
        current_month_25_str = current_month_25.strftime('%Y-%m-%d')
        last_month_25_str = last_month_25.strftime('%Y-%m-%d')

 
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from payroll where iduser=? and month=? and year=?"
    values=(decode_id(current_user.idinformationuser),month,year)
    cursor.execute(sql,values)
    payroll=cursor.fetchone()
    conn.commit()
    conn.close()
    form_method=await request.form()
    if 'exportpdf' in form_method and form_method.get("exportpdf")=="exportpdf":
        pdf_content = exportfilepdf(request,decode_id(current_user.idinformationuser),month,year)
        response = Response(pdf_content)
        filepath=f'payroll'+str(decode_id(current_user.idinformationuser)
        
        )+'.pdf'
        response.headers["Content-Disposition"] = f"attachment; filename={filepath}"
        response.headers["Content-Type"] = "application/pdf"

        return response
    return RedirectResponse(url=f"/payrollemployee/{form_method.get("month")}/{form_method.get("year")}",status_code=status.HTTP_302_FOUND)

@payroll.get("/createallowancemain",tags=['payroll'], response_class=HTMLResponse)
async def createallowancemain(request:Request,current_user: User = Depends(get_current_user_from_token)):
    current_date = datetime.now()

    # Lấy tháng và năm hiện tại
    current_month = current_date.month
    current_year = current_date.year
    return RedirectResponse(url=f"/createallowance/{current_month}/{current_year}",status_code=status.HTTP_302_FOUND)

@payroll.get("/createallowance/{month}/{year}",tags=['payroll'], response_class=HTMLResponse)
async def createallowance_get(request:Request,month,year,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="""
    SELECT id,email
FROM informationUser
WHERE id NOT IN (SELECT iduser FROM Allowance where month=? and year=?);"""
    value=(month,year)
    cursor.execute(sql,value)
    email_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    emaillist=[(email[0],email[1])for email in email_temp]

    conn=db.connection()
    cursor=conn.cursor()
    sql="select a.*,i.Email,i.Fullname from  Allowance a join informationUser i on i.id=a.iduser where a.month=? and a.year=?"
    value=(month,year)
    cursor.execute(sql,value)
    listalowance_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    listalowance=[(a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7],a[11],a[12])for a in listalowance_temp]
    context={
        "request":request,
        "current_user":current_user,
        "image_path":request.cookies.get("image_path_session"),
        "roleuser":request.cookies.get("roleuser"),
        "fullname":request.cookies.get("fullname_session"),
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession"),
        "year":year,
        "month":month,
        "emaillist":emaillist,
        "listalowance":listalowance
        
    }
    return templates.TemplateResponse("payroll/createallowance.html",context)


@payroll.post("/createallowance/{month}/{year}",tags=['payroll'], response_class=HTMLResponse)
async def createallowance(request:Request,month,year,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="""
    SELECT id,email
FROM informationUser
WHERE id NOT IN (SELECT iduser FROM Allowance where month=? and year=?);"""
    value=(month,year)
    cursor.execute(sql,value)
    email_temp=cursor.fetchall()
    conn.commit()
    conn.close()
    emaillist=[(email[0],email[1])for email in email_temp]
    form_method=await request.form()
    if "yearform" in form_method and form_method.get("yearform")=="yearform":
        return RedirectResponse(url=f"/createallowance/{form_method["month"]}/{form_method["year"]}",status_code=status.HTTP_302_FOUND)
    elif "addallowance" in form_method and form_method.get("addallowance")=="addallowance":
        conn=db.connection()
        cursor=conn.cursor()
        sql="SELECT * FROM Allowance where iduser=? and month=? and year=?"
        value=(form_method["email"],month,year)
        cursor.execute(sql,value)
        temp=cursor.fetchone()
        conn.commit()
        conn.close()
        if temp:
            conn=db.connection()
            cursor=conn.cursor()
            sql="""
            update Allowance set Internet_Allowance=?,Meal_Allowance=?,Phone_Allowance=?,Transportation_Allowance=?,
    Other_Cash_Allowance=?,Year_End_Bonus=?,Unused_Annual_Leave=? wherew iduser=? and month=? and year=?"""
            value=(form_method["Internet_Allowance"],form_method["Meal_Allowance"],form_method["Phone_Allowance"]
                ,form_method["Transportation_Allowance"],form_method["Other_Cash_Allowance"],
                form_method["Year_End_Bonus"],form_method["Unused_Annual_Leave"],form_method["email"],month,year)
            cursor.execute(sql,value)
            conn.commit()
            conn.close()
        else:
            conn=db.connection()
            cursor=conn.cursor()
            sql="""
            insert into Allowance(Internet_Allowance,Meal_Allowance,Phone_Allowance,Transportation_Allowance,
    Other_Cash_Allowance,Year_End_Bonus,Unused_Annual_Leave,iduser,month,year) values(?,?,?,?,?,?,?,?,?,?)"""
            value=(form_method["Internet_Allowance"],form_method["Meal_Allowance"],form_method["Phone_Allowance"]
                ,form_method["Transportation_Allowance"],form_method["Other_Cash_Allowance"],
                form_method["Year_End_Bonus"],form_method["Unused_Annual_Leave"],form_method["email"],month,year)
            cursor.execute(sql,value)
            conn.commit()
            conn.close()
        return RedirectResponse(url=f"/createallowance/{month}/{year}",status_code=status.HTTP_302_FOUND)