from typing import List
from typing import Optional

from fastapi import Request
class roleForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.role: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.role = form.get(
            "role"
        )  # since outh works on username field we are considering email as username
    
    async def is_valid(self):
        if not self.role :
            self.errors.append("role is required")
        if not self.errors:
            return True
        return False
    
class SelectionForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.selection: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.selection = form.get(
            "selection"
        )  # since outh works on username field we are considering email as username

class groupuserForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.group: Optional[str] = None
        self.alias: Optional[str] = None
        self.email: Optional[str] = None
        self.url: Optional[str] = None
        self.description: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.group = form.get("group")  
        self.alias = form.get("alias")  
        self.email = form.get("email")  
        self.url = form.get("url")  
        self.description = form.get("description")  
    
    async def is_valid(self):
        if not self.group :
            self.errors.append("group is required")
        if not self.alias :
            self.errors.append("alias is required")
        if not self.email :
            self.errors.append("email is required")
        if not self.url :
            self.errors.append("url is required")
        if not self.description :
            self.errors.append("description is required")
        if not self.errors:
            return True
        return False