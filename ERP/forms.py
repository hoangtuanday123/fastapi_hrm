from typing import List
from typing import Optional

from fastapi import Request
from pydantic import BaseModel
from datetime import date
class addtaskweeklytimesheetForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.project: Optional[str] = None
        self.component: Optional[str] = None
        self.task: Optional[str] = None
        self.enddate: Optional[date] = None

    async def load_data(self):
        form = await self.request.form()
        self.project = form.get("project") 
        self.component = form.get("component")
        self.task = form.get("task")
        self.enddate = form.get("enddate")
    
    async def is_valid(self):
        if not self.project :
            self.errors.append("project is required")
        if not self.task :
            self.errors.append("task is required")
        if not self.enddate :
            self.errors.append("enddate is required")
        if not self.errors:
            return True
        return False