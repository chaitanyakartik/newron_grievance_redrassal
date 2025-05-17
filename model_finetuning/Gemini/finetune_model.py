import google.auth
from google.auth.transport.requests import AuthorizedSession

PROJECT_ID = "newron-stage"
LOCATION = "us-central1"

credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
authed_session = AuthorizedSession(credentials)

endpoint = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/tuningJobs"

payload = {
    "baseModel": "gemini-2.0-flash-001",
    "supervisedTuningSpec": {
        "trainingDatasetUri": "gs://grievance-redressal-train-data/train_data.jsonl",
        "validationDatasetUri": "gs://grievance-redressal-train-data/test_data.jsonl",
    },
    "tunedModelDisplayName": "tuned_gemini_example",
}

response = authed_session.post(endpoint, json=payload)

print(response.status_code)
print(response.json())
