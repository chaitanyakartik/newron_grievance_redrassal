from google.cloud import aiplatform

aiplatform.init(project="myproject", location="us-central1")

tuning_job = aiplatform.TuningJob.create(
    display_name="tuned_gemini",
    base_model="gemini-2.0-flash-001",
    training_dataset_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-2_0/text/sft_train_data.jsonl",
    validation_dataset_uri="gs://cloud-samples-data/ai-platform/generative_ai/gemini-2_0/text/sft_validation_data.jsonl",
)

print(f"Tuning job started: {tuning_job.resource_name}")
