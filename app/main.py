from fastpi import fastpi, HTTPexception
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Collumn, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import re

app = fastpi(title="Sistema de Padronização de Nomes e Emails")

