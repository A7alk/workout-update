from langflow.load import run_flow_from_json
from dotenv import load_dotenv
import requests
from typing import Optional
import json
import os

load_dotenv()

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "0230cce6-f2c0-4ab4-877a-a1911b63d67e"
APPLICATION_TOKEN = os.getenv("LANGFLOW_TOKEN")


def dict_to_string(obj, level=0):
    strings = []
    indent = "  " * level  # Indentation for nested levels
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                nested_string = dict_to_string(value, level + 1)
                strings.append(f"{indent}{key}: {nested_string}")
            else:
                strings.append(f"{indent}{key}: {value}")
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            nested_string = dict_to_string(item, level + 1)
            strings.append(f"{indent}Item {idx + 1}: {nested_string}")
    else:
        strings.append(f"{indent}{obj}")

    return ", ".join(strings)


def ask_ai(profile, user_question):
    try:
        # Ensure the file name matches your uploaded file exactly
        result = run_flow_from_json(flow="askai.json.scpt",
                                    inputs={"profile": profile, "question": user_question})
        return result
    except FileNotFoundError:
        return "Error: The required JSON file 'askai.json.scpt' is missing."
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def get_macros(profile, goals):
    TWEAKS = {
        "TextInput-PR5Jb": {
            "input_value": ", ".join(goals)
        },
        "TextInput-PrfY9": {
            "input_value": dict_to_string(profile)
        }
    }
    return run_flow("", tweaks=TWEAKS, application_token=APPLICATION_TOKEN)


def run_flow(message: str,
             output_type: str = "chat",
             input_type: str = "chat",
             tweaks: Optional[dict] = None,
             application_token: Optional[str] = None) -> dict:
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/macros"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if application_token:
        headers = {"Authorization": f"Bearer {application_token}", "Content-Type": "application/json"}
    
    response = requests.post(api_url, json=payload, headers=headers)

    # Check the response before parsing
    if response.status_code != 200:
        print(f"API Error: {response.status_code} - {response.text}")
        return {"error": "API request failed"}
    
    try:
        # Log full response for debugging
        data = response.json()
        print("API Response:", data)

        # Safely retrieve nested values with `.get()`
        outputs = data.get("outputs", [{}])
        if outputs:
            results_text = outputs[0].get("outputs", [{}])[0].get("results", {}).get("text", {}).get("data", {}).get("text", "No text found")
            return json.loads(results_text)
        else:
            return "Error: No outputs found in API response."
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
        print(f"Error parsing response: {e}")
        print(f"Response data: {data}")  # Log full response for troubleshooting
        return "Error: Unable to retrieve macro data."

