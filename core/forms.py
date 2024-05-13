from typing import List
from typing import Optional
from datetime import date
from fastapi import Request
from pydantic import BaseModel
from fastapi import Request
from pydantic import BaseModel
from typing import List, Optional
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2.credentials import Credentials
from urllib.parse import urlparse, parse_qs
import os.path
import io
import shutil
import pickle
from mimetypes import MimeTypes

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
   
    
    def __init__(self,idcontract,LaborcontractNo,Laborcontracttype,Laborcontractterm,Commencementdate,Position,Employeelevel,dayoff):
       
        self.idcontract=idcontract
        self.LaborcontractNo=LaborcontractNo
        self.Laborcontracttype=Laborcontracttype
        self.Laborcontractterm=Laborcontractterm
        self.Commencementdate=Commencementdate
        self.Position=Position
        self.Employeelevel=Employeelevel
        self.dayoff=dayoff
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
        self.dayoff: Optional[int] = None
        
    
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
    
class EditForm:
    def __init__(self, request: Request, col: str):
        self.request: Request = request
        self.errors: List = []
        setattr(self, col, None)  

    async def load_data(self, col: str):
        form = await self.request.form()
        setattr(self, col, form.get(col))
 

class CCCDForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.front_cccd: Optional[str] = None
        self.back_cccd: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.front_cccd = form.get("fileCCCD_front")
        self.back_cccd = form.get("fileCCCD_back")


class AvatarForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.file: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.file = form.get("avatar")

class HCCForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.file: Optional[str] = None
        self.documentname: Optional[str] = None
        self.notarized: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.file = form.get("filehcc")
        self.documentname = form.get("documentname")
        if form.get("notarized") == "Yes":
            self.notarized = '1'
        else:
            self.notarized = '0'

class EducationForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.file: Optional[str] = None
        self.type: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.file = form.get("fileeducation")
        self.type = form.get("typeDegree")

class QualificationForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.file: Optional[str] = None
        self.type: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.file = form.get("filequalification")
        self.type = form.get("typeQualification")
        
class DriveAPI:
    # Define the scopes
    SCOPES = ['https://www.googleapis.com/auth/drive']
    file_id = ""

    def __init__(self):
        """Initialize the DriveAPI instance."""
        self.creds = self.authenticate()
        self.service = build('drive', 'v3', credentials=self.creds)

        # Request a list of first N files or folders with name and id from the API.
        # results = self.service.files().list(pageSize=100, fields="files(id, name)").execute()
        # self.files = results.get('files', [])

    def authenticate(self):
        """Authenticate and authorize the user."""
        creds = None
        # The file token.pickle stores the user's access and refresh tokens.
        # It is created automatically when the authorization flow completes for the first time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials are available, request the user to log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the access token in token.pickle file for future usage
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return creds

    def print_files(self):
        """Print a list of files."""
        print("Here's a list of files:")
        for file in self.files:
            print(f"File Name: {file['name']}, File ID: {file['id']}")

    def download_file(self, file_id, file_name):
        """Download a file from Google Drive."""
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()

        # Initialize a downloader object to download the file
        downloader = MediaIoBaseDownload(fh, request, chunksize=204800)
        done = False

        try:
            # Download the data in chunks
            while not done:
                status, done = downloader.next_chunk()

            fh.seek(0)

            # Write the received data to the file
            with open(file_name, 'wb') as f:
                shutil.copyfileobj(fh, f)

            print("File Downloaded")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def upload_file(self, filepath):
        """Upload a file to Google Drive."""
        global file_id
        # Extract the file name out of the file path
        name = os.path.basename(filepath)

        # Find the MimeType of the file
        mime_type, _ = MimeTypes().guess_type(name)
        mime_type = mime_type or 'application/octet-stream'

        # Create file metadata
        file_metadata = {'name': name}

        media = MediaFileUpload(filepath, mimetype=mime_type)

        try:
            # Create a new file in the Drive storage
            file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            file_id = file['id']
            print(f"File uploaded. File ID: {file['id']}")
        except Exception as e:
            print(f"Error: {e}")

    def get_link_file_url(self):
        global file_id
        print("file id is:" + file_id)
        file_url = self.service.files().get(fileId=file_id, fields="webContentLink").execute()
        # # Find the index of ':' and '}'
        # start_index = file_url.find(':') + 1
        # end_index = file_url.rfind('}')
        # file_url=file_url[start_index:end_index].strip()
        return file_url


 
        