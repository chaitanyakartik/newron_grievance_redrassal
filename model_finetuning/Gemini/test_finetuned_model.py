import json
import os
import time
from google.cloud import aiplatform
from dotenv import load_dotenv

load_dotenv()

# Set your project details
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")
TUNED_ENDPOINT_ID = os.getenv("TUNED_ENDPOINT_ID")  # e.g., "3493514578816401408"
BASE_MODEL = "gemini-2.0-flash-001"  # Or use gemini-1.5-pro if needed

# Auth and client setup
aiplatform.init(project=PROJECT_ID, location=LOCATION)

# Path to your validation set
VALIDATION_FILE_PATH = "/Users/chaitanyakartik/Projects/Newron_GR/model_finetuning/OpenAI/test.jsonl"

def get_prediction_from_endpoint(endpoint_id, user_message):
    endpoint = aiplatform.Endpoint(endpoint_name=f"projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/{endpoint_id}")
    response = endpoint.predict(instances=[{"messages": [{"role": "user", "content": user_message}]}])
    return response.predictions[0]['candidates'][0]['content']

def get_prediction_from_gemini_base(user_message, model=BASE_MODEL):
    from vertexai.preview.generative_models import GenerativeModel, ChatSession
    model = GenerativeModel(model)
    chat = model.start_chat()
    response = chat.send_message(user_message)
    return response.text.strip()

def load_validation_data(path):
    with open(path, "r") as f:
        for line in f:
            yield json.loads(line)

def evaluate_model(predict_func, validation_data, label=""):
    total = 0
    correct = 0
    for entry in validation_data:
        user_msg = next(m['content'] for m in entry['messages'] if m['role'] == 'user')
        expected = next(m['content'] for m in entry['messages'] if m['role'] == 'assistant')

        try:
            pred = predict_func(user_msg)
        except Exception as e:
            print(f"Prediction failed: {e}")
            continue

        if pred.lower() == expected.lower():
            correct += 1
            print("Correct\n")
        else:
            print("Incorrect\n")
            print(f"Expected: {expected}")
            print(f"Predicted: {pred}\n")
        total += 1
    accuracy = correct / total if total else 0
    print(f"\n{label} Accuracy: {accuracy:.2%}")
    return accuracy

if __name__ == "__main__":
    validation_data = list(load_validation_data(VALIDATION_FILE_PATH))[0:2]

    print("Evaluating fine-tuned Gemini model...")
    start_time = time.time()
    evaluate_model(lambda msg: get_prediction_from_endpoint(TUNED_ENDPOINT_ID, msg), validation_data, label="Tuned Model")
    print(f"Time taken (tuned): {time.time() - start_time:.2f} seconds\n")

    print("Evaluating base Gemini model...")
    start_time = time.time()
    evaluate_model(lambda msg: get_prediction_from_gemini_base(msg), validation_data, label="Base Model")
    print(f"Time taken (base): {time.time() - start_time:.2f} seconds")
