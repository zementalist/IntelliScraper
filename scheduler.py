import threading
import schedule
import time
import asyncio
from datetime import datetime, timedelta
from database.models import Job, FrequencyType, get_session
# from app import scrape_social, get_session

class ScheduleTask():
    # def __init__(self, name, next_exec_time, criteria, company_ids, freq):
    #     self.name = name
    #     self.next_exec_time = next_exec_time
    #     self.criteria = criteria
    #     self.company_ids = company_ids
    #     self.freq = freq
    #     self.thread = None

    def __init__(self, job:Job, callback):
        # self.frequency = job.frequency._value_
        # self.next_exec_time = str(job.next_exec_time)
        # self.company_id = job.company_id
        # self.company_url = job.company_url
        # self.items_count = job.items_count
        # self.publish_date_limit = job.publish_date_limit
        # self.social_platform_name = job.social_platform_name._value_
        self.job = job
        self.companies = list(self.job.companies)
        self.name = f"{self.companies[0].company_url.split('wiki/')[-1]}"
        self.criteria = {
            self.job.social_platform_name._value_: {
                "enabled":True,
                "publishDateEnd":self.job.publish_date_limit,
                "itemCount": self.job.items_count
            }
        }
        self.callback = callback
        # super(ScheduleTask, self).__init__(**kwargs)
        
    def get_task(self):
        if self.job.frequency._value_ == FrequencyType.once.value:
            self.thread = threading.Timer(self.get_time_diff(), self.task_wrapper)
        elif self.job.frequency._value_ == FrequencyType.daily.value:
            self.thread = threading.Timer(self.get_time_diff_daily(), self.task_wrapper)
        elif self.job.frequency._value_ == FrequencyType.weekly.value:
            self.thread = threading.Timer(self.get_time_diff_weekly(), self.task_wrapper)
        self.thread.start()
        return self

    def edit_task(self, next_exec_time):
        self.job.next_exec_time = next_exec_time
        self.thread.cancel()
        if self.job.frequency._value_ == FrequencyType.once.value:
            self.thread = threading.Timer(self.get_time_diff(), self.task_wrapper)
        elif self.job.frequency._value_ == FrequencyType.daily.value:
            print("DAILY THREAD EDITED ", self.get_time_diff_daily())
            self.thread = threading.Timer(self.get_time_diff_daily(), self.task_wrapper)
        elif self.job.frequency._value_ == FrequencyType.weekly.value:
            self.thread = threading.Timer(self.get_time_diff_weekly(), self.task_wrapper)
        self.thread.start()

    def delete_task(self):
        if self.thread is not None:
            self.thread.cancel()
        del scheduled_tasks[self.name]

    def task_wrapper(self):
        companies_ids = list(map(lambda company: company.company_id, self.job.companies))

        asyncio.run(self.callback(self.criteria, companies_ids))
        # if self.job.frequency._value_ == FrequencyType.once.value:
        #     self.delete_task()
            # self.edit_task(get_next_day(self.job.next_exec_time))
        if self.job.frequency._value_ == FrequencyType.daily.value:
            print("EDIT DAILY")
            self.edit_task(get_next_day(self.job.next_exec_time))
        elif self.job.frequency._value_ == FrequencyType.weekly.value:
            self.edit_task(get_next_week(self.job.next_exec_time))

    def get_time_diff(self):
        now = time.time()
        scheduled_time = time.mktime(time.strptime(str(self.job.next_exec_time), "%Y-%m-%d %H:%M:%S"))
        if scheduled_time < now:
            scheduled_time += 86400  # add 1 day if scheduled time is in the past
        return scheduled_time - now

    def get_time_diff_daily(self):
        now = time.time()
        next_day = get_next_day(self.job.next_exec_time)
        scheduled_time = time.mktime(time.strptime(next_day, "%Y-%m-%d %H:%M:%S"))
        if scheduled_time < now:
            scheduled_time += 86400  # add 1 day if scheduled time is in the past
        return scheduled_time - now

    def get_time_diff_weekly(self):
        now = time.time()
        next_week = get_next_week(self.job.next_exec_time)
        scheduled_time = time.mktime(time.strptime(next_week, "%Y-%m-%d %H:%M:%S"))
        if scheduled_time < now:
            scheduled_time += 604800  # add 1 week if scheduled time is in the past
        return scheduled_time - now


# Define a function to scrape social media
# def scrape_social(criteria, company_ids):
#     print(f"Scraping social media for {criteria} and company IDs: {company_ids}")


# Define a function to get the next daily scheduled time
def get_next_day(next_exec_time):
    next_day = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.mktime(time.strptime(str(next_exec_time), '%Y-%m-%d %H:%M:%S')) + 10))
    return next_day

# Define a function to get the next weekly scheduled time
def get_next_week(next_exec_time):
    next_week = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.mktime(time.strptime(str(next_exec_time), '%Y-%m-%d %H:%M:%S')) + 604800))
    return next_week


# Define a dictionary to store scheduled tasks

# # Add some example tasks to the dictionary
# task1 = ScheduleTask('task1', '2023-05-22 14:11:30', 'social media', ['123', '456'], 'once')
# task2 = ScheduleTask('task2', '2023-05-22 14:11:20', 'banking', ['789'], 'once')
# task1.add_task()
# task2.add_task()

# # Main loop to run the scheduled tasks
# def startJobs(jobs ,callback):
#     for job in jobs:
#         # Modify execution time to run the task now
#         # job.next_exec_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         task = ScheduleTask(job, callback)
#         task.add_task()
#         print("Added job " + task.job.company_url + " to start at " + str(task.job.next_exec_time))
#     while True:
#         schedule.run_pending()
#         print("RUNNING")
#         print(schedule.get_jobs())
#         time.sleep(1)

