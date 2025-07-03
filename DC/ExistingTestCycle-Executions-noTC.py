import requests
from requests.auth import HTTPBasicAuth
import time


######## REPLACE ME
# Replace with your basic auth credentials
username = ''
password = ''

####### REPLACE ME
#  Replace with your host
host = ''

######## REPLACE ME
# Define the cycle key you want to update
testRunKey = ''

# API endpoint template for creating a test case
test_case_url = f'{host}/rest/atm/1.0/testcase'

# API endpoint template for posting test results
test_results_url_template = f'{host}/rest/atm/1.0/testrun/{testRunKey}/testcase/{{}}/testresult'

# Headers
headers = {
    'Content-Type': 'application/json'
}


####REPLACE ME
# Test case data if no test case exists
test_case_data = {
    "projectKey": "ZULU",  # Ensure this matches the test results
    "name": "ZULU automated TC",  # This can be dynamic or predefined
    "customFields": {
        "checkbox": "true"  # Modify the custom field as needed, ensure the value type matches what the API expects
    }
}

# Test result data, we could pull this from a JUnitXML and parse the results.
test_results = [
    {
        "status": "Fail",
        "testCaseKey": "JQA-T1234",  # Fail test case key for iteration
        "comment": "Test failed due to an error."
    },
    {
        "status": "Pass",
        "testCaseKey": "ZULU-T302",  # Pass test case key for validation
        "comment": "Test passed successfully."
    }
]

# Function to create the test case if not found
def create_test_case(test_case_key):
    # Adjust test case name dynamically if needed
    test_case_data["name"] = f"ZULU automated TC {test_case_key}"  # You can modify this to be dynamic if required
    print(f"Attempting to create test case with key: {test_case_key}")
    
    # Send POST request to create the test case
    response = requests.post(test_case_url, json=test_case_data, headers=headers, auth=HTTPBasicAuth(username, password))

    if response.status_code == 201:
        response_data = response.json()
        test_case_key = response_data['key']
        print(f"Test case created with key: {test_case_key}")
        return test_case_key
    else:
        # Print detailed error for debugging
        print(f"Error creating test case: {response.status_code} - {response.content}")
        print(f"Request Payload: {test_case_data}")
        return None

# Function to post test results
def post_test_results(test_case_key, test_result_data):
    # Construct URL for specific test case
    url = test_results_url_template.format(test_case_key)

    print(f"Attempting to post test result for {test_case_key}")

    # Send the POST request to add the test results
    response = requests.post(url, json=test_result_data, headers=headers, auth=HTTPBasicAuth(username, password))

    # Print response status
    if response.status_code == 201:
        print(f'Successfully added test result for {test_case_key}: {response.content}')
        return True
    elif response.status_code == 400:
        print(f"400 Error: Test case {test_case_key} not found. Retrying with test case creation...")
        return False
    else:
        print(f'Error adding test results for {test_case_key}: {response.status_code} - {response.content}')
        return False

# Function to iterate and retry on failure
def process_test_results():
    print("Starting to process test results...")
    
    # Retry logic for posting test results
    for test_result in test_results:
        test_case_key = test_result["testCaseKey"]
        print(f"\nProcessing test case {test_case_key}...")

        # First, attempt to post the test result
        if not post_test_results(test_case_key, test_result):
            # If test case does not exist (400 error), create it and retry
            print(f"Test case {test_case_key} not found, creating it...")
            test_case_key = create_test_case(test_case_key)
            if test_case_key:
                # After creating the test case, retry posting the test result
                print(f"Retrying to post test result for {test_case_key}...")
                post_test_results(test_case_key, test_result)
            time.sleep(2)  # Adding a delay before retrying
        else:
            print(f"Test result posted successfully for {test_case_key}")

# Start processing test results
process_test_results()
