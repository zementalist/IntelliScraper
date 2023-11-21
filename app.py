from fastapi import FastAPI, HTTPException, Query, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from scheduler import ScheduleTask
from datetime import datetime, timedelta

import pandas as pd
import os
import time
import schedule
import unicodedata

from threading import Thread
from typing import Annotated, List
from math import nan

from pydantic import BaseModel

# from action import ActionFactory

from scheduler import ScheduleTask

from fastapi_sqlalchemy import DBSessionMiddleware
from database.models import get_session, User, UserCreate, Job, Company, JobCompany
from sqlmodel import Session, select

app = FastAPI()
ActionFactory = None
app.mount("/assets", StaticFiles(directory="portal\dist\\assets"), name="assets")

app.add_middleware(DBSessionMiddleware, db_url="sqlite:///is_db_0910.db")
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"])

scheduled_tasks = {}

# @app.get("/scrape_operators_info", summary="Scrape operators to get operators info and social media links for now.")
# def scrape_operators_info():
#     try:
#         operators_info_scraper.crawl_operators_info()
#         return({"Status": 'done!'})
#     except Exception as e:
#         raise HTTPException(status_code=503, detail=str(e))

@app.get("/get_companies", summary="Get the list of selected companies.")
def get_companies(countries_list:Annotated[list[str], Query()]=[], industries_list:Annotated[list[str], Query()]=[], session: Session = Depends(get_session)):
    def process_df(df):
        # Input: Pandas.DataFrame
        # Process: Re-format data (flatten arrays & limit long results, etc..)
        # Return: Pandas.DataFrame
        # df.columns = [col.lower() for col in df.columns]


        # Replace nullable URLs
        # df['operator_wiki_url'] = df['operator_wiki_url'].replace({"https://null.abc.efg":""})
        # df['official_website'] = df['official_website'].replace({"https://null.abc.efg":""})


        # Limit long list values
        # target_columns = ['emails', 'numbers']
        # n_limit_values = 4
        # for column in target_columns:
        #     df[column] = df[column].str[:n_limit_values]

        # Split lists into strings (i.e. ['a', 'b'] => a, b)
        # target_columns = ['product', 'industry', 'emails', 'numbers']
        # for column in target_columns:
        #     df[column] = df[column].str.join(" | ")
        df = df.drop(columns="product")

        # Rename columns
        df.columns = df.columns.str.replace("_", " ").str.capitalize()

        # Replace NaN since they block JSON from encoding
        df = df.replace(nan, "")

        

        return df

    try:
        # D:\Projects\IntelliScraper\core\data\scraped\all_operators.json
        # storage_path = os.path.join(os.path.dirname(
        #     os.path.dirname(os.path.abspath(__file__))))
        # file_path = r"{}".format(os.path.join(storage_path, '\core\data\scraped\all_operators.json'))
        # df = pd.read_json(file_path)
        # df = pd.read_json(r'.\core\services\data\scraped_data\all_operators.json')
        
        # TODO: Don't forget to add industries filter
        result = None
        # # result = df[df.country.str.lower().isin([x.lower() for x in countries_list])]
        # if countries_list:
        #     result = df[df.country.str.lower().str.contains(fr"{'|'.join(countries_list).lower()}")]
        # if industries_list:
        #     if result is not None:
        #         df = result
        #     result = df[df.industry.str.lower().str.contains(fr"{'|'.join(industries_list).lower()}")]
        # if result is not None:
        #     result = process_df(result)
        #     result = result.to_dict('records')
        # result = session.exec(select(Company).where(Company.c.country.in_(["Egypt"]))).all()
        query = select(
            Company.id,
            Company.country,
            Company.headquarter,
            Company.sector,
            Company.operator_wiki_url,
            Company.company_name,
            Company.official_website,
            Company.founded,
            Company.industry,
            Company.facebook,
            Company.twitter,
            Company.instagram,
            Company.linkedin,
            Company.youtube,
            Company.tiktok,
            Company.numbers,
            Company.emails,
            )
        
        if len(countries_list) > 0:
            query = query.filter(Company.country.in_(countries_list))
        if len(industries_list) > 0:
            query = query.filter(Company.industry.in_(industries_list))
        result = session.execute(query).all()
        return({"success": 1, 'result':result})
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_countries")
def getCountries():
    df = pd.read_json(r'.\core\services\data\scraped_data\all_operators.json')
    try:
        countries = list(df.country.unique())
        countries = sorted(countries)
        success = True
    except Exception as e:
        print(str(e))
        countries = None
        success = False
    
    return ({
        "result": countries,
        "success": success
    })


@app.get("/get_industries")
def getCountries():
    df = pd.read_json(r'.\core\services\data\scraped_data\all_operators.json')
    try:
        industries = list(df.industry.unique())
        industries = sorted(industries)
        success = True
    except Exception as e:
        industries = None
        success = False
    
    return ({
        "result": industries,
        "success": success
    })

@app.post("/scrape_social")
async def scrape_social(criteria:dict, company_ids:list):
    print("Hello World")
    print(criteria)
    print(company_ids)
    message = "Error:"
    if len(company_ids)  < 1:
        message = " No companies were selected."
    if len(criteria.keys()) < 1:
        message += " No scraping criteria provided."
    try:
        result = {}
        # storage_path = os.path.join(os.path.dirname(
        #     os.path.dirname(os.path.abspath(__file__))), 'data', 'scraped_data').replace('\\scrapers\\basic_info', '')
        # file_path = r"{}".format(os.path.join(storage_path, 'all_operators.json'))
        # df = pd.read_json(file_path)
        df = pd.read_json(r'.\core\data\scraped_data\all_operators.json')

        companies = df[df['id'].isin(company_ids)]
        for criterionName in criteria:
            criterion = criteria[criterionName]
            print("WORKING ON: " + criterionName)
            for company in companies.to_dict("records"):
                print(company["company_name"])
                social_platform_name = criterionName.lower()
                if company["company_name"] not in result:
                    result[company['company_name']] = {}
                if social_platform_name in companies.columns and company[social_platform_name] is not None and criterion['enabled']:
                    n_items = criterion['itemCount']
                    publish_date_end = criterion['publishDateEnd']
                    action = ActionFactory().make(social_platform_name, n_items, publish_date_end)
                    # TODO: Multithreading execution
                    data = action.execute(company[social_platform_name]) # [{offer: "",  satisfaction_rate:%}]
                    result[company['company_name']][social_platform_name] = data
        print("FINAL RESULT")
        print(result)
    except Exception as e:
        raise Exception(e)
    return({"success":True, "result":result})

@app.on_event("startup")
async def startup_event(session:Session=next(get_session())):

    def import_action_factory():
        global ActionFactory
        action = __import__("action")
        ActionFactory = action.ActionFactory
    action_factory_import_thread = Thread(target=import_action_factory)
    action_factory_import_thread.start()

    # jobs_thread = Thread(target=start_scheduler, kwargs={"session":next(get_session())})
    # jobs_thread.start()

    # Add companies to Database
    # migrate_companies_to_db(session)

    print("Jobs Thread Started")

    # # The following code to create a job with 2 companies

    # job = Job(
    #     # company_id=6769,
    #     # company_url="https://en.wikipedia.org/wiki/Telecom_Egypt",
    #     social_platform_name="youtube",
    #     items_count=1,
    #     publish_date_limit=None,
    #     frequency="daily",
    #     output_format_type="filesystem"
    # )
        
    # session.add(job)
    # session.commit()
    # session.refresh(job)

    # job_company = JobCompany(
    #     company_id=7565,
    #     company_url="https://en.wikipedia.org/wiki/Telecom_Egypt",
    #     job_id=job.id
    # )
    # job_company2 = JobCompany(
    #     company_id=3233,
    #     company_url="https://en.wikipedia.org/wiki/Zain_Saudi_Arabia",
    #     job_id=job.id
    # )
    # session.add(job_company)
    # session.add(job_company2)
    # session.commit()
    # session.refresh(job_company)
    # session.refresh(job_company2)
    # job = session.get(Job, 1)
    # print(job.companies)
    session.close()

@app.get("/")
def home():
    response= FileResponse("portal\dist\index.html")
    return response
    #return({"message": "System is up!"})

def start_scheduler(session:Session):
    # job = Job(
    #     company_id=6769,
    #     company_url="https://en.wikipedia.org/wiki/Telecom_Egypt",
    #     social_platform_name="youtube",
    #     items_count=4,
    #     publish_date_limit=None,
    #     frequency="daily",
    #     output_format_type="filesystem"
    # )
    # session.add(job)
    # session.commit()
    # session.refresh(job)
    # print(job)
    job = session.get(Job, 1)
    if job is not None:
        next_exec_time = (datetime.now() + timedelta(0, 3)).isoformat(sep=" ", timespec="seconds")
        job.next_exec_time = datetime.fromisoformat(next_exec_time)
        job.items_count = 1
        jobs = [job]
        for job in jobs:
            task = ScheduleTask(job, scrape_social)
            scheduled_tasks[task.name] = task.get_task()
            print("Added job " + task.name + " to start at " + str(task.job.next_exec_time))
    while True:
        schedule.run_pending()
        time.sleep(1)
    return({"message":"System is up!"})


@app.get("/jobs")
def get_jobs(session:Session=Depends(get_session)):
    # jobs = session.execute(select(
    #     Job.id,
    #     Job.social_platform_name,
    #     Job.items_count,
    #     Job.publish_date_limit,
    #     Job.frequency,
    #     Job.output_format_type,
    #     Job.next_exec_time,
    #     Job.created_on,
    #     Job.updated_at,
    # ).filter(Job.is_deleted == False))
    jobs = session.query(Job).all()
    desired_order_list = ["id", "social_platform_name", "items_count", "publish_date_limit", "frequency", "output_format_type", "next_exec_time", "created_on", "updated_at"]
    # Append jobs & merge company names
    results = []
    for job in jobs:
        print(job)
        singleJob = job.dict()
        singleJob = {k: singleJob[k] for k in desired_order_list}

        singleJob["companies"] = ", ".join([company.operator_wiki_url.split("/wiki")[-1] for company in job.companies])
        results.append(singleJob)
    session.close()
    return({"results": results})

@app.post("/job/delete/{id}")
def delete_job(id:int, session:Session=Depends(get_session)):
    print("DELETING ", id)
    job = session.get(Job, id)
    results = 0
    if job is not None:
        job_companies = session.exec(select(JobCompany).where(JobCompany.job_id == id))
        session.delete(job)
        for j_c in job_companies:
            session.delete(j_c)

        session.commit()
        print("Job is deleted")
        results = 1
    
    return {"results":results}

@app.post("/insert_jobs", summary="Insert new Jobs")
async def insert_jobs(payload: dict = Body(...), session:Session=Depends(get_session)):
    # print(jobs)
    companies_ids = payload["companies_ids"]
    jobs = payload["jobs"]
    # df = pd.read_json(r'.\core\services\data\scraped_data\all_operators.json')
    # companies = session.exec(select(Company).where(Company.id in companies_ids))
    companies = session.query(Company).filter(Company.id.in_(companies_ids)).all()
    for j in jobs:
        job = Job(**j)
        session.add(job)
        session.commit()
        session.refresh(job)

        task = ScheduleTask(job, scrape_social)
        scheduled_tasks[task.name] = task.get_task()
        
        for company in companies:
            job_company = JobCompany(
                company_id=company.id,
                company_url=company.operator_wiki_url,
                job_id=job.id
            )
            session.add(job_company)
    session.commit()
    session.close()
    return {"results":1}
    

def migrate_companies_to_db(session: Session):
    def ud(text):
        return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore')

    df = pd.read_json(r'.\core\data\scraped\all_operators.json')
    # df = df.replace(to_replace="\u00", value='')
    df = df.replace(to_replace=nan, value="")
    df['founded'] = pd.to_numeric(df['founded'], errors='coerce')
    for record in df.to_dict("records"):
        del record['product']
        del record['founded']
        del record['id']
        record['company_name'] = ud(record['company_name']).decode("utf-8")
        record['page_last_edit_date'] = datetime.fromisoformat(record['page_last_edit_date'])
        if type(record['official_website']) == list:
            record['official_website'] = record['official_website'][0]
        company = Company(**record)
        session.add(company)
    session.commit()