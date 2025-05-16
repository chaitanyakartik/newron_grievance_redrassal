from google.cloud import aiplatform

# Set your project and location
PROJECT_ID = "myproject"
LOCATION = "us-central1"

def list_tuning_jobs():
    aiplatform.init(project=PROJECT_ID, location=LOCATION)

    # List all tuning jobs in the location
    tuning_jobs = aiplatform.TuningJob.list()

    if not tuning_jobs:
        print("No tuning jobs found.")
        return

    for job in tuning_jobs:
        print(f"Name: {job.resource_name}")
        print(f"Display Name: {job.display_name}")
        print(f"State: {job.state.name}")  # Job state enum, e.g. JOB_STATE_SUCCEEDED
        print(f"Create Time: {job.create_time}")
        print(f"Update Time: {job.update_time}")
        print("-" * 40)

if __name__ == "__main__":
    list_tuning_jobs()


def get_tuning_job_status(tuning_job_name: str):
    aiplatform.init(project=PROJECT_ID, location=LOCATION)

    tuning_job = aiplatform.TuningJob(tuning_job_name)
    print(f"Job: {tuning_job.resource_name}")
    print(f"Display Name: {tuning_job.display_name}")
    print(f"State: {tuning_job.state.name}")
    print(f"Create Time: {tuning_job.create_time}")
    print(f"Update Time: {tuning_job.update_time}")


get_tuning_job_status("projects/myproject/locations/us-central1/tuningJobs/1234567890123456789")
