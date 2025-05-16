from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv("Openai_api_key")
os.environ["OPENAI_API_KEY"]=openai_api_key

client = OpenAI()

job_id = "ftjob-YfCitBFp8HQn5UvuybRvcLrV"

jobs = client.fine_tuning.jobs.list()
for job in jobs.data:
    if job.id == job_id:
        print(job.status)
        break
