from typing import List
from typing import Optional
from datetime import date
from fastapi import Request
from pydantic import BaseModel

from validation.models import informationUser


class informationUserForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.Fullname: Optional[str] = None
        self.Nickname: Optional[str] = None
        self.Email: Optional[str] = None
        self.Contactaddress: Optional[str] = None
        self.IdUserAccount: Optional[str] = None
        self.Phone: Optional[str] = None
        self.LinkedIn: Optional[str] = None
        self.Years: Optional[str] = None
        self.Location: Optional[str] = None
        self.Maritalstatus: Optional[str] = None
        self.Ethnicgroup: Optional[str] = None
        self.Religion: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.Fullname = form.get(
            "Fullname"
        )  # since outh works on username field we are considering email as username
        self.Nickname = form.get("Nickname")
        self.Email = form.get("Email")
        self.Contactaddress = form.get("Contactaddress")
        self.IdUserAccount = form.get("IdUserAccount")
        self.Phone = form.get("Phone")
        self.LinkedIn = form.get("LinkedIn")
        self.Years = form.get("Years")
        self.Location = form.get("Location")
        self.Maritalstatus = form.get("Maritalstatus")
        self.Ethnicgroup = form.get("Ethnicgroup")
        self.Religion = form.get("Religion")
    
    async def is_valid(self):
        if not self.Email or not (self.Email.__contains__("@")):
            self.errors.append("Email is required")
        if not self.Fullname :
            self.errors.append("Fullnamr is required")
        # if not self.Contactaddress :
        #     self.errors.append("Contactaddress is required")
        # if not self.Phone :
        #     self.errors.append("Phone is required")
        if not self.errors:
            return True
        return False


class latestEmploymentForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.Employer: Optional[str] = None
        self.Jobtittle: Optional[str] = None
        self.AnnualSalary: Optional[str] = None
        self.AnnualBonus: Optional[str] = None
        self.RetentionBonus: Optional[str] = None
        self.RetentionBonusExpiredDate: Optional[date] = None
        self.StockOption: Optional[str] = None
        self.StartDate: Optional[date] = None
        self.EndDate: Optional[date] = None
        self.IdInformationUser: Optional[str] = None
    
    async def load_data(self):
        form = await self.request.form()
        self.Employer = form.get(
            "Employer"
        )  # since outh works on username field we are considering email as username
        self.Jobtittle = form.get("Jobtittle")
        self.AnnualSalary = form.get("AnnualSalary")
        self.AnnualBonus = form.get("AnnualBonus")
        self.RetentionBonus = form.get("RetentionBonus")
        self.RetentionBonusExpiredDate = form.get("RetentionBonusExpiredDate")
        self.StockOption = form.get("StockOption")
        self.StartDate = form.get("StartDate")
        self.IdInformationUser = form.get("IdInformationUser")
        self.EndDate = form.get("EndDate")
        

class usercccdForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.No: Optional[str] = None
        self.FullName: Optional[str] = None
        self.DateOfbirth: Optional[date] = None
        self.PlaceOfBirth: Optional[str] = None
        self.Address: Optional[str] = None
        self.IssueOn: Optional[date] = None
        self.IdInformationUser: Optional[date] = None
    
    async def load_data(self):
        form = await self.request.form()
        self.No = form.get(
            "No"
        )  # since outh works on username field we are considering email as username
        self.DateOfbirth = form.get("DateOfbirth")
        self.PlaceOfBirth = form.get("PlaceOfBirth")
        self.Address = form.get("Address")
        self.IssueOn = form.get("IssueOn")
        self.IdInformationUser = form.get("IdInformationUser")
        

    




