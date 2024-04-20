from typing import List
from typing import Optional
from datetime import date
from fastapi import Request
from pydantic import BaseModel
class informationUserJob:
    def __init__(self, EmployeeNo, Companysitecode, Department, Directmanager, Workforcetype, Workingphone, Workingemail,
                 Bankaccount, Bankname, Taxcode, Socialinsurancecode, Healthinsurancecardcode, Registeredhospitalname,
                 Registeredhospitalcode):
        self.EmployeeNo = EmployeeNo
        self.Companysitecode = Companysitecode
        self.Department = Department
        self.Directmanager = Directmanager
        self.Workforcetype = Workforcetype
        self.Workingphone = Workingphone
        self.Workingemail = Workingemail
        self.Bankaccount = Bankaccount
        self.Bankname = Bankname
        self.Taxcode = Taxcode
        self.Socialinsurancecode = Socialinsurancecode
        self.Healthinsurancecardcode = Healthinsurancecardcode
        self.Registeredhospitalname = Registeredhospitalname
        self.Registeredhospitalcode = Registeredhospitalcode

class laborContract():
   
    
    def __init__(self,idcontract,LaborcontractNo,Laborcontracttype,Laborcontractterm,Commencementdate,Position,Employeelevel):
       
        self.idcontract=idcontract
        self.LaborcontractNo=LaborcontractNo
        self.Laborcontracttype=Laborcontracttype
        self.Laborcontractterm=Laborcontractterm
        self.Commencementdate=Commencementdate
        self.Position=Position
        self.Employeelevel=Employeelevel
class forexsalary():
 
    
    def __init__(self ,Forex,Annualsalary,Monthlysalary,
    Monthlysalaryincontract,Quaterlybonustarget,Annualbonustarget):
       
        self.Forex=Forex
        self.Annualsalary=Annualsalary
        self.Monthlysalary=Monthlysalary
        self.Monthlysalaryincontract=Monthlysalaryincontract
        self.Quaterlybonustarget=Quaterlybonustarget
        self.Annualbonustarget=Annualbonustarget

class EmployeeRelativeForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.Relationship: Optional[str] = None
        self.phone: Optional[str] = None
        self.email: Optional[str] = None
        self.contactaddress: Optional[str] = None
        self.career: Optional[str] = None
        self.citizenIdentificationNo: Optional[str] = None
        self.fullname: Optional[str] = None
        self.dateofbirth : Optional[date] = None
        self.placeofbirth : Optional[str] = None
        self.address : Optional[str] = None
        self.issued : Optional[date] = None
    
    async def load_data(self):
        form = await self.request.form()
        self.Relationship = form.get(
            "Relationship"
        )  # since outh works on username field we are considering email as username
        self.phone = form.get("phone")
        self.email = form.get("email")
        self.contactaddress = form.get("contactaddress")
        self.career = form.get("career")
        self.citizenIdentificationNo = form.get("citizenIdentificationNo")
        self.fullname = form.get("fullname")
        self.dateofbirth = form.get("dateofbirth")
        self.placeofbirth = form.get("placeofbirth")
        self.address = form.get("address")
        self.issued = form.get("issued")
    

class laborcontractForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.Laborcontracttype: Optional[str] = None
        self.Laborcontractterm: Optional[str] = None
        self.Commencementdate: Optional[date] = None
        self.Position: Optional[str] = None
        self.Employeelevel: Optional[str] = None
        
    
    async def load_data(self):
        form = await self.request.form()
        self.Laborcontracttype = form.get(
            "Laborcontracttype"
        )  # since outh works on username field we are considering email as username
        self.Laborcontractterm = form.get("Laborcontractterm")
        self.Commencementdate = form.get("Commencementdate")
        self.Position = form.get("Position")
        self.Employeelevel = form.get("Employeelevel")
    async def is_valid(self):
        if not self.Laborcontracttype :
            self.errors.append("Laborcontracttype is required")
        if not self.Laborcontractterm :
            self.errors.append("Laborcontractterm is required")
        if not self.Commencementdate:  # corrected condition here
            self.errors.append("Commencementdate is required")
        if not self.Position :
            self.errors.append("Position is required")
        if not self.Employeelevel:  # corrected condition here
            self.errors.append("Employeelevel is required")
        if not self.errors:
            return True
        return False
    
class forexsalaryForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.forextype: Optional[str] = None
        self.Annualsalary: Optional[str] = None
        self.Monthlysalary: Optional[date] = None
        self.Monthlysalaryincontract: Optional[str] = None
        self.Quaterlybonustarget: Optional[str] = None
        self.Annualbonustarget: Optional[str] = None
        
    
    async def load_data(self):
        form = await self.request.form()
        self.forextype = form.get(
            "forextype"
        )  # since outh works on username field we are considering email as username
        self.Annualsalary = form.get("Annualsalary")
        self.Monthlysalary = form.get("Monthlysalary")
        self.Monthlysalaryincontract = form.get("Monthlysalaryincontract")
        self.Quaterlybonustarget = form.get("Quaterlybonustarget")
        self.Annualbonustarget = form.get("Annualbonustarget")
    async def is_valid(self):
        if not self.forextype :
            self.errors.append("forextype is required")
        if not self.Annualsalary :
            self.errors.append("Annualsalary is required")
        if not self.Monthlysalary:  # corrected condition here
            self.errors.append("Monthlysalary is required")
        if not self.Monthlysalaryincontract :
            self.errors.append("Monthlysalaryincontract is required")
        if not self.Quaterlybonustarget:  # corrected condition here
            self.errors.append("Quaterlybonustarget is required")
        if not self.Annualbonustarget:  # corrected condition here
            self.errors.append("Annualbonustarget is required")
        if not self.errors:
            return True
        return False
 
        