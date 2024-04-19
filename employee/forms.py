from typing import List
from typing import Optional
from datetime import date
from fastapi import Request
from pydantic import BaseModel

class Employeeinformation(FlaskForm):
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.companysitecode: Optional[str] = None
        self.department: Optional[str] = None
        self.directmanager: Optional[str] = None
        self.Contactaddress: Optional[str] = None
        self.workfortype: Optional[str] = None
        self.Bankaccount: Optional[str] = None
        self.Taxcode: Optional[str] = None
        self.Socialinsurancecode: Optional[str] = None
        self.Healthinsurancecardcode: Optional[str] = None
        self.Registeredhospitalname: Optional[str] = None
        self.Registeredhospitalcode: Optional[str] = None
        
    async def load_data(self):
        form = await self.request.form()
        self.companysitecode = form.get(
            "companysitecode"
        )  # since outh works on username field we are considering email as username
        self.department = form.get("department")
        self.directmanager = form.get("directmanager")
        self.Contactaddress = form.get("Contactaddress")
        self.workfortype = form.get("workfortype")
        self.Bankaccount = form.get("Bankaccount")
        self.Taxcode = form.get("LinkedIn")
        self.Socialinsurancecode = form.get("Years")
        self.Healthinsurancecardcode = form.get("Location")
        self.Registeredhospitalname = form.get("Maritalstatus")
        self.Registeredhospitalcode = form.get("Ethnicgroup")
    