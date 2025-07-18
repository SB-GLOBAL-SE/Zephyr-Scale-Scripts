import requests
import json

# === CONFIGURATION ===
BASE_URL = "https://api.zephyrscale.smartbear.com/v2"
BEARER_TOKEN = ""
TEST_CASE_KEY = ""

# === HEADERS ===
headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

# === STEP 1: Get Test Executions for the Test Case ===
executions_url = f"{BASE_URL}/testexecutions"
params = {"testCase": TEST_CASE_KEY}

response = requests.get(executions_url, headers=headers, params=params)

if response.status_code != 200:
    print(f"Error fetching test executions: {response.status_code} - {response.text}")
    exit(1)

executions = response.json().get("values", [])
if not executions:
    print("No test executions found for this test case.")
    exit(0)

print(f"Found {len(executions)} executions for test case {TEST_CASE_KEY}")

# === STEP 2: For Each Execution, Get Test Steps ===
for execution in executions:
    execution_id = execution.get("id")
    print(f"\n=== Test Execution ID: {execution_id} ===")

    steps_url = f"{BASE_URL}/testexecutions/{execution_id}/teststeps"
    steps_response = requests.get(steps_url, headers=headers, params={"maxResults": 1000})

    if steps_response.status_code != 200:
        print(f"  Error fetching steps: {steps_response.status_code} - {steps_response.text}")
        continue

    try:
        steps_data = steps_response.json()
    except Exception as e:
        print(f"  Failed to parse JSON: {e}")
        print(f"  Raw response: {steps_response.text}")
        continue

    steps = steps_data.get("values", [])

    if not steps:
        print("  No steps returned in 'values'. Full raw response for debugging:")
        print(json.dumps(steps_data, indent=2))
        continue

    # === STEP 3: Print Raw Step and GET Status from 'self' ===
    for idx, step in enumerate(steps, start=1):
        inline = step.get("inline", {})
        print(f"\n  Step #{idx} Raw:")
        print(json.dumps({"inline": inline}, indent=2))  # Show only 'inline'

        # Lookup status via 'self' link
        status = inline.get("status", {})
        status_url = status.get("self")
        if status_url:
            status_response = requests.get(status_url, headers=headers)
            if status_response.status_code == 200:
                status_name = status_response.json().get("name", "UNKNOWN")
                print(f'\n  GET self: "{status_name}"')
            else:
                print(f'\n  GET self: ERROR {status_response.status_code}')
        else:
            print('\n  GET self: Not available')
