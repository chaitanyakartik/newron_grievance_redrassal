import requests
import os
from openai import OpenAI

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv("Openai_api_key")
os.environ["OPENAI_API_KEY"]=openai_api_key

headers = {
    "Authorization": f"Bearer {openai_api_key}"
}

#check for current finetuning jobs
response = requests.get("https://api.openai.com/v1/fine_tuning/jobs", headers=headers)
print(response.status_code)
print(response.json())



# client = OpenAI()

# # Upload training file
# with open("/Users/chaitanyakartik/Projects/Newron_GR/data/Fine_Tuning_data/PM_Kisan/train.jsonl", "rb") as f:
#     train_file = client.files.create(
#         file=f,
#         purpose="fine-tune"
#     )

# # Upload validation file
# with open("/Users/chaitanyakartik/Projects/Newron_GR/data/Fine_Tuning_data/PM_Kisan/test.jsonl", "rb") as f:
#     validation_file = client.files.create(
#         file=f,
#         purpose="fine-tune"
#     )

# # Start fine-tuning job
# fine_tune_job = client.fine_tuning.jobs.create(
#     training_file=train_file.id,
#     validation_file=validation_file.id,
#     model="gpt-3.5-turbo",
#     hyperparameters={
#         "n_epochs": 2
#     },
#     suffix="grievance-classifier-v1"
# )


# print(f"Fine-tuning job started. ID: {fine_tune_job.id}")
# print(fine_tune_job)
