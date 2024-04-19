from datetime import datetime, timedelta
from typing import Union, Any
from fastapi import FastAPI, HTTPException,Depends
from dotenv import load_dotenv,dotenv_values
from pydantic import BaseModel
from authentication.views import auth
from core.views import core_bp
from validation.views import validate
from candidate.views import candidate 
from admin.views import admin
from employee.views import employee
from ERP.views import ERP
from decouple import Config, RepositoryEnv
from fastapi.staticfiles import StaticFiles





import os
#from config.config import Config
app = FastAPI(
    title='FastAPI JWT', openapi_url='/openapi.json', docs_url='/docs',
    description='fastapi jwt'
)
app.mount("/static", StaticFiles(directory="static"), name="static")



load_dotenv()
config = Config(RepositoryEnv(".env"))


app.include_router(auth)
app.include_router(core_bp)
app.include_router(validate)
app.include_router(candidate)
app.include_router(admin)
app.include_router(ERP)
app.include_router(employee)
