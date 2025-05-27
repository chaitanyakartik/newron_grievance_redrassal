import requests

# Define the API endpoint
url = "http://34.93.126.124:8000/classify"  # Replace with the actual URL if deployed elsewhere

# Define the test payload
payload = {
    "query": "I need help with my PM-KISAN application.",
    "history": [
        {"role": "user", "content": "I submitted my application but it hasn't been processed."},
        {"role": "assistant", "content": "Can you provide more details about your application?"}
    ],
    "dept_path": ["AGRICULTURE DEPARTMENT"]
}

# Send a POST request to the endpoint
try:
    response = requests.post(url, json=payload)

    # Print the response
    if response.status_code == 200:
        print("Success!")
        print("Response:", response.json())
    else:
        print("Failed!")
        print("Status Code:", response.status_code)
        print("Response:", response.text)
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")