import google.auth
from google.auth.transport.requests import AuthorizedSession

PROJECT_ID = "573969935641"
LOCATION = "us-central1"
TUNING_JOB_ID = "6988361370588676096"

credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
authed_session = AuthorizedSession(credentials)

endpoint = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/tuningJobs/{TUNING_JOB_ID}"

response = authed_session.get(endpoint)
print(response.status_code)
print(response.json())
