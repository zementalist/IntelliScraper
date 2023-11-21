from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column ,Integer, String, TIMESTAMP, text, Date,DateTime, Enum, Boolean

from pydantic import root_validator

from sqlmodel import Field, ForeignKey, SQLModel, Session, create_engine, Relationship
from sqlmodel.main import BaseModel

from typing import Optional, List
from datetime import datetime

import configparser
import enum

# Declare Base class, used for alembic to track models.classes and DB.tables
Base = declarative_base()

# Replace SQLModel metadata with SQLAlchemy metadata
metadata = Base.metadata
SQLModel.metadata = metadata

# Set Base class for models as SQLModel 
# (it already inherits SQLAlchemy.Base & Pydantic.BaseModel)
Base = SQLModel

# Read Configuration to get DB connection string
config = configparser.ConfigParser()
config.read("alembic.ini")
DATABASE_URL = config.get("alembic", "sqlalchemy.url")

# Initialize SQLite engine
engine = create_engine(DATABASE_URL)


# ______ Define Models _______


# Enum for Role Type (no tables created)
class RoleType(enum.Enum):
    user = "user"
    admin = "admin"


# Enum for Job Frequency Type (no tables created)
class FrequencyType(enum.Enum):
    once = "once"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

# Social Platforms (No tables)
class SocialPlatform(enum.Enum):
    twitter = "twitter"
    youtube = "youtube"
    facebook = "facebook"
    tiktok = "tiktok"
    instagram = "instagram"
    telegram = "telegram"

class DataFormatType(enum.Enum):
    filesystem = "filesystem"
    database = "database"

# User Base
# those are the attributes needed to create a user
# And used to receive input from HTTP Requests (email, password)
class UserBase(SQLModel):
    email:str = Field(String, max_length=255)
    password: str = Field(String, max_length=255)

# User model
class User(UserBase, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(sa_column=Column("id", Integer, primary_key=True, autoincrement=True, index=True))
    created_on:Optional[datetime] = Field(sa_column=Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")))
    updated_at:Optional[datetime] = Field(sa_column=Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), server_onupdate=text("CURRENT_TIMESTAMP")))
    last_login_at: Optional[datetime] = Field(sa_column=Column(TIMESTAMP))
    role: RoleType = Field(sa_column=Column(Enum(RoleType), default=RoleType.user))

    def __str__(self):
        return f"id = {self.id},\nemail = {self.email},\ncreated_on = {self.created_on},\nupdated_on = {self.updated_at}"


# This class is used as bridge between HTTP request body/data
# to insert new user to DB
class UserCreate(UserBase):
    pass


class JobCompany(SQLModel, table=True):
    __tablename__ = "companies_jobs"
    # id: Optional[int] = Field(sa_column=Column("id", Integer, primary_key=True, autoincrement=True))
    company_id: Optional[int] =  Field(default=None, foreign_key="companies.id", primary_key=True)
    # company_url: str = Field(String, max_length=255, nullable=False)
    job_id: Optional[int] = Field(default=None, foreign_key="jobs.id", primary_key=True)

    # job: Optional[Job] = Relationship(back_populates="companies_jobs")
    # company: Optional[Company] = Relationship(back_populates="companies_jobs")


# Job Model
class Job(SQLModel, table=True):
    __tablename__ = "jobs"

    id: Optional[int] = Field(sa_column=Column("id", Integer, primary_key=True, autoincrement=True, index=True))
    # company_id: int = Field(sa_column=Column("company_id", Integer))
    # company_url: str = Field(String, max_length=255, nullable=False)
    social_platform_name: SocialPlatform = Field(sa_column=Column(Enum(SocialPlatform), nullable=False))
    items_count: Optional[int] = Field(Integer, nullable=True)
    publish_date_limit: Optional[datetime] = Field(sa_column=Column(Date, nullable=True))
    frequency: FrequencyType = Field(sa_column=Column(Enum(FrequencyType), nullable=False))
    next_exec_time: Optional[datetime] = Field(sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP")))
    output_format_type: DataFormatType = Field(sa_column=Column(Enum(DataFormatType), nullable=False))
    created_on:Optional[datetime] = Field(sa_column=Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")))
    updated_at:Optional[datetime] = Field(sa_column=Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), server_onupdate=text("CURRENT_TIMESTAMP")))
    is_deleted: bool = Field(sa_column=Column(Boolean, nullable=False, default=False, server_default=text("0")))
    
    companies:List["Company"] = Relationship(back_populates="jobs", link_model=JobCompany)

    # Check that (items_count) and (publish_date_limit) at least one is provided (not None)
    @root_validator(pre=True)
    def check_itemsCount_pubDateLimit_one_exist(cls, values):
        items_count = values.get("items_count")
        publish_date_limit = values.get("publish_date_limit")
        if items_count is None and publish_date_limit is None:
            raise ValueError("Provide at least Items Count or Publish Date Limit")
        return values


class Company(SQLModel, table=True):
    __tablename__ = "companies"
    id: Optional[int] = Field(sa_column=Column("id", Integer, primary_key=True, autoincrement=True))
    country: str = Field(String, max_length=255, nullable=False)
    headquarter: str = Field(String, max_length=255, nullable=False)
    operator_wiki_url: str = Field(String, max_length=255, nullable=False)
    company_name: Optional[str] = Field(String, max_length=255, nullable=True)
    founded: Optional[int] = Field(sa_column=Column('founded', Integer, default=None, nullable=True))
    industry: Optional[str] = Field(String, max_length=255, nullable=True)
    sector: Optional[str] = Field(String, max_length=255, nullable=True)
    numbers: Optional[str] = Field(String, nullable=True)
    emails: Optional[str] = Field(String, nullable=True)
    official_website: Optional[str] = Field(String, nullable=False)
    page_last_edit_date: Optional[datetime] = Field(sa_column=Column(TIMESTAMP, nullable=True))
    facebook: Optional[str] = Field(String, nullable=True)
    twitter: Optional[str] = Field(String, nullable=True)
    instagram: Optional[str] = Field(String, nullable=True)
    linkedin: Optional[str] = Field(String, nullable=True)
    youtube: Optional[str] = Field(String, nullable=True)
    tiktok: Optional[str] = Field(String, nullable=True)

    jobs:List[Job] = Relationship(back_populates="companies", link_model=JobCompany)




# This function returns a session item to perform CRUD on DB
# and is used by dependency injection in FastAPI routing/endpoints
def get_session():
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()