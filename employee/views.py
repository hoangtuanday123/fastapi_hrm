import db
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from authentication.models import get_current_user_from_cookie,get_current_user_from_token
from authentication.models import User
from ultils import file_path_default,encode_id,decode_id
templates = Jinja2Templates(directory="templates")
employee = APIRouter()

_image_path = ""
_fullname = ""
_roleuser = "employee"
_informationuserjobid = ""
_roleadmin = ""
_image_path_admin = ""
_fullname_admin = ""

@employee.get("/employeepage/{image_path}/{fullname}", response_class=HTMLResponse)

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
    