import db
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse,FileResponse,StreamingResponse
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from authentication.models import get_current_user_from_cookie,get_current_user_from_token
from authentication.models import User
templates = Jinja2Templates(directory="templates")
exception=APIRouter()

@exception.get('/exception',tags=['Exception'], response_class=HTMLResponse)
async def exception_get(request: Request,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor=conn.cursor()
    sql="select * from Exception where status=1"
    cursor.execute(sql)
    excep=cursor.fetchone()
    conn.commit()
    conn.close()
    context={
        "request":request,
        "image_path_admin":request.cookies.get("image_path_adminsession"),
        "roleadmin":request.cookies.get("roleadmin"),
        "fullname_admin":request.cookies.get("fullname_adminsession"),
        "roleuser":request.cookies.get("roleuser"),
        "current_user":current_user,
        "excep":excep
    }
    return templates.TemplateResponse("exception/exception.html",context)

@exception.post('/exception',tags=['Exception'], response_class=HTMLResponse)
async def exception_post(request: Request,current_user: User = Depends(get_current_user_from_token)):
    form_method=await request.form()
    conn=db.connection()
    cursor=conn.cursor()
    sql="update Exception set luongcoso=%s,vung1=%s,vung2=%s,vung3=%s,vung4=%s,giacanhbanthan=%s,giacanhnguoiphuthuoc=%s "
    value=(form_method["basicsalary"],form_method["companysitecode1"],form_method["companysitecode2"],
           form_method["companysitecode3"],form_method["companysitecode4"],form_method["PersonalDeduction"],
           form_method["DependentsDeduction"],)
    cursor.execute(sql,value)
    conn.commit()
    conn.close()
    return RedirectResponse(url="/exception",status_code=status.HTTP_302_FOUND)
