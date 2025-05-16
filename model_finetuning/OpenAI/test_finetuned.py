import json
from openai import OpenAI
import os
import time

from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv("Openai_api_key")
os.environ["OPENAI_API_KEY"]=openai_api_key

client = OpenAI()

# Replace this with your fine-tuned model name from the fine-tune job output
finetuned_model_name = "ft:gpt-3.5-turbo-0125:newron-ai:grievance-classifier-v1:BXqdxPFw"
finetuned_model_name_v2 = "ft:gpt-4o-mini-2024-07-18:newron-ai:grievance-classifier-v2:BXstPr1J"

# Base model to compare against
base_model_name = "gpt-3.5-turbo-0125"
base_model_name_v2 = "gpt-4o-mini-2024-07-18"


validation_file_path = "/Users/chaitanyakartik/Projects/Newron_GR/data/Fine_Tuning_data/PM_Kisan/test.jsonl"

grivience_list=[
    
]
def get_model_response(model_name, user_message):
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": user_message}],
        max_tokens=100,
        temperature=0,
        stop=None,
    )
    # Assuming the model outputs a single message completion
    return response.choices[0].message.content.strip()

def load_validation_data(path):
    with open(path, "r") as f:
        for line in f:
            yield json.loads(line)

def evaluate_model(model_name, validation_data):
    total = 0
    correct = 0
    for entry in validation_data:
        user_msg = next(m['content'] for m in entry['messages'] if m['role'] == 'user')
        expected = next(m['content'] for m in entry['messages'] if m['role'] == 'assistant')

        pred = get_model_response(model_name, user_msg)

        # Simple exact match accuracy; you can enhance with fuzzy matching if needed
        if pred.lower() == str(expected).lower() :
            correct += 1
            print("Correct\n")
        else:
            print("Incorrect\n")
            # If you want to see the incorrect predictions
            print(f"Expected: {expected}")
            print(f"Predicted: {pred}\n")
        total += 1
    accuracy = correct / total if total else 0
    return accuracy

if __name__ == "__main__":
    validation_data = list(load_validation_data(validation_file_path))  # Only 2 entries

    print("Evaluating fine-tuned model...")
    start_time = time.time()
    finetuned_acc = evaluate_model(finetuned_model_name_v2, validation_data)
    elapsed = time.time() - start_time
    print(f"Fine-tuned model accuracy: {finetuned_acc:.2%}")
    print(f"Time taken (fine-tuned): {elapsed:.2f} seconds")

    print("\nEvaluating base model...")
    start_time = time.time()
    base_acc = evaluate_model(base_model_name_v2, validation_data)
    elapsed = time.time() - start_time
    print(f"Base model accuracy: {base_acc:.2%}")
    print(f"Time taken (base): {elapsed:.2f} seconds")

    # print(get_model_response(base_model_name, validation_data[0]['messages'][0]['content']))

