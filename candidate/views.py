import db
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from authentication.models import get_current_user_from_cookie,get_current_user_from_token
from authentication.models import User
from ultils import file_path_default,encode_id,decode_id
templates = Jinja2Templates(directory="templates")

candidate=APIRouter()
@candidate.get('/candidate/{image_path}/{fullname}', response_class=HTMLResponse)
def candidatepage_get(request: Request,image_path, fullname,current_user: User = Depends(get_current_user_from_token)):
   
    conn=db.connection()
    cursor1=conn.cursor()
    sql1="select * from informationUser where id_useraccount=?"
    value1=(decode_id(current_user.id))
    cursor1.execute(sql1,value1)
    user_temp=cursor1.fetchone()
    context={
        "request":request,
        "roleuser":"candidate",
        "image_path":image_path,
        "fullname":fullname,
        "current_user":current_user,
        "idinformationuser":user_temp[0]
    }
    return templates.TemplateResponse("candidate/candidatepage.html",context)
    #return render_template("candidate/candidatepage.html",roleuser="candidate",image_path=image_path,fullname=fullname,idinformationuser=user_temp[0])

@candidate.post('/candidate/{image_path}/{fullname}', response_class=HTMLResponse)
def candidatepage(request: Request,image_path, fullname,current_user: User = Depends(get_current_user_from_token)):
    conn=db.connection()
    cursor1=conn.cursor()
    sql1="select * from informationUser where id_useraccount=?"
    value1=(decode_id(current_user.id))
    cursor1.execute(sql1,value1)
    user_temp=cursor1.fetchone()
    context={
        "request":request,
        "roleuser":"candidate",
        "image_path":image_path,
        "fullname":fullname,
        "current_user":current_user,
        "idinformationuser":encode_id(user_temp[0])
    }
    return templates.TemplateResponse("candidate/candidatepage.html",context)