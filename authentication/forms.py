from typing import List
from typing import Optional

from fastapi import Request
from pydantic import BaseModel

class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.email: Optional[str] = None
        self.password: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.email = form.get(
            "email"
        )  # since outh works on username field we are considering email as username
        self.password = form.get("password")

    async def is_valid(self):
        if not self.email or not (self.email.__contains__("@")):
            self.errors.append("Email is required")
        if not self.password or not len(self.password) >= 4:
            self.errors.append("A valid password is required")
        if not self.errors:
            return True
        return False
    
class RegisterForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.email: Optional[str] = None
        self.password: Optional[str] = None
        self.confirm: Optional[str] = None
    
    async def load_data(self):
        form = await self.request.form()
        self.email = form.get(
            "email"
        )  # since outh works on username field we are considering email as username
        self.password = form.get("password")
        self.confirm = form.get("confirm")  # corrected assignment here
    
    async def is_valid(self):
        if not self.email or not (self.email.__contains__("@")):
            self.errors.append("Email is required")
        if not self.password or not len(self.password) >= 4:
            self.errors.append("A valid password is required")
        if self.password != self.confirm:  # corrected condition here
            self.errors.append("Password is not duplicated")
        if not self.errors:
            return True
        return False
    
class TwoFactorForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.otp: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.otp = form.get(
            "otp"
        )  # since outh works on username field we are considering email as username
    
    async def is_valid(self):
        if not self.otp :
            self.errors.append("otp is required")
        if not self.errors:
            return True
        return False
    
    
class ForgotPasswordForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.email: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.email = form.get(
            "email"
        )
    async def is_valid(self):
        if not self.email or not (self.email.__contains__("@")):
            self.errors.append("Email is required")
        if not self.errors:
            return True
        return False

class ChangePasswordForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.password: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.password = form.get(
            "password"
        )
    
    async def is_valid(self):
        if not self.password or not len(self.password) >= 4:
            self.errors.append("A valid password is required")
        if not self.errors:
            return True
        return False
