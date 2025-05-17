import google.auth
from google.auth.transport.requests import Request
import requests

credentials, project_id = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
credentials.refresh(Request())
access_token = credentials.token

print(f"\n✅ Authenticated as: {getattr(credentials, 'service_account_email', 'user account')}")
print(f"✅ Project ID: {project_id}")

permissions_to_test = [
    "aiplatform.tuningJobs.list",
    "aiplatform.tuningJobs.create",
    "aiplatform.models.upload",
    "aiplatform.models.list",
]

url = f"https://cloudresourcemanager.googleapis.com/v1/projects/{project_id}:testIamPermissions"

response = requests.post(
    url,
    headers={"Authorization": f"Bearer {access_token}"},
    json={"permissions": permissions_to_test}
)

print("\n🔍 Vertex AI Permissions:")
if response.status_code == 200:
    granted = response.json().get("permissions", [])
    for p in permissions_to_test:
        print(f" - {p}: {'✅' if p in granted else '❌'}")
else:
    print(f"❌ Error {response.status_code}: {response.text}")










# grievance-redressal-train-data


# gsutil cp /Users/chaitanyakartik/Projects/Newron_GR/model_finetuning/Gemini/train_gemini.jsonl gs://grievance-redressal-train-data/train_data.jsonl
# gsutil cp /Users/chaitanyakartik/Projects/Newron_GR/model_finetuning/Gemini/test_gemini.jsonl gs://grievance-redressal-train-data/test_data.jsonl


# gs://grievance-redressal-train-data/test_data.jsonl
# gs://grievance-redressal-train-data/train_data.jsonl