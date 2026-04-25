import requests


def set_api_key(url, api_key):
    headers = {'Content-Type': 'application/json'}
    data = {'api_key': api_key}
    response = requests.post(url, json=data, headers=headers)
    try:
        print(f"Setting API Key...\nResponse: {response.json()}\n")
    except requests.exceptions.JSONDecodeError:
        print(f"Failed to set API Key. Response: {response.text}\n")

def set_interview_protocol_index(url, interview_protocol_index):
    headers = {'Content-Type': 'application/json'}
    data = {'interview_protocol_index': interview_protocol_index}
    response = requests.post(url, json=data, headers=headers)
    print(f"Setting interview protocol index...\nResponse: {response.json()}\n")

def test_set_prompt(url, prompt_type, prompt):
    headers = {'Content-Type': 'application/json'}
    data = {prompt_type: prompt}
    response = requests.post(url, json=data, headers=headers)
    try:
        print(
            f"Testing set_{prompt_type}: '{prompt}'\nResponse: {response.json()}\n")
    except requests.exceptions.JSONDecodeError:
        print(
            f"Testing set_{prompt_type}: '{prompt}'\nResponse: {response.text}\n")


def test_get_welcome_message(url):
    response = requests.post(url)
    try:
        response_data = response.json()
        print(f"Testing get_welcome_message:\nResponse: {response_data}\n")
    except requests.exceptions.JSONDecodeError:
        print(f"Testing get_welcome_message:\nResponse: {response.text}\n")


def test_get_doctor_response(url):
    while True:
        patient_prompt = input(
            "Enter patient response (type 'exit' to finish): ")
        if patient_prompt.lower() == 'exit':
            break
        headers = {'Content-Type': 'application/json'}
        data = {'patient_prompt': patient_prompt}
        response = requests.post(url, json=data, headers=headers)
        try:
            response_data = response.json()
            print(
                f"Testing get_doctor_response with prompt: '{patient_prompt}'\nResponse: {response_data}\n")
        except requests.exceptions.JSONDecodeError:
            print(
                f"Testing get_doctor_response with prompt: '{patient_prompt}'\nResponse: {response.text}\n")


# base_url = "https://llm4socialisolation-fd4082d0a518.herokuapp.com"

base_url = "http://127.0.0.1:8080"

set_api_key(f"{base_url}/api/set-key",
            "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")

set_interview_protocol_index(f"{base_url}/api/set-interview-protocol_index", None)

# test_set_prompt(f"{base_url}/prompts/system",
#                 "system_prompt", "You are a student asking professor question. Be like a student and greet the prof")

# test_set_prompt(f"{base_url}/prompts/emotion", "emotion_prompt", None)

# test_set_prompt(f"{base_url}/prompts/therapy-strategy",
#                 "therapy_strategy_prompt", ".")

test_get_welcome_message(f"{base_url}/responses/welcome")

test_get_doctor_response(f"{base_url}/responses/doctor")

test_get_welcome_message(f"{base_url}/responses/welcome")

set_interview_protocol_index(f"{base_url}/api/set-interview-protocol_index", 3)

test_get_doctor_response(f"{base_url}/responses/doctor")