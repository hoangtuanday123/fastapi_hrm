from typing import List
from typing import Optional

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


# class latestEmploymentForm(FlaskForm):
#     Employer = StringField("Employer", validators=[InputRequired(message='Employer name is required')])
#     Jobtittle = StringField("Jobtittle")
#     AnnualSalary = IntegerField("AnnualSalary")
#     AnnualBonus = IntegerField("AnnualBonus")
#     RetentionBonus = IntegerField("RetentionBonus")
#     RetentionBonusExpiredDate = DateTimeField("RetentionBonusExpiredDate")
#     StockOption = IntegerField("StockOption")
#     StartDate = DateTimeField("StartDate")
#     EndDate = DateTimeField("EndDate")
#     IdInformationUser = IntegerField("IdInformationUser")

# class usercccdForm(FlaskForm):
#     No = IntegerField("No", validators=[InputRequired(message='Citizen Identification No is required')])
#     FullName = StringField("Full Name", validators=[InputRequired(message='Full Name is required')])
#     DateOfbirth = DateTimeField("Date Of Birth")
#     PlaceOfBirth = StringField("Place Of Birth")
#     Address = StringField("Address")
#     IssueOn = DateTimeField("Issue On")
#     IdInformationUser = IntegerField("IdInformationUser")




