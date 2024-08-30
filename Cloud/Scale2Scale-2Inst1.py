import requests
import io
import sys
import json

def migrateTC(source_base_url, source_bearer_token, target_base_url, target_bearer_token):
    # URL to fetch test cases from the source instance
    url = f'{source_base_url}/testcases?startAt=1&maxResults=1'

    # Headers for source instance
    source_headers = {
        'Authorization': f'Bearer {source_bearer_token}'
    }

    response = requests.get(url, headers=source_headers)
    targetProjectKey = 'APPS'
    old_tc_keys = []
    new_tc_keys = []  # List to store all new test case keys

    if response.status_code == 200:
        payload_io = io.StringIO(response.text)
        
        # Read and save the payload content
        payload_content = payload_io.getvalue()
        with open("payload_output.json", "w") as file:
            file.write(payload_content)
        
        data = json.loads(payload_content)
        
        # Headers for target instance
        target_headers = {
            'Authorization': f'Bearer {target_bearer_token}',
            'Content-Type': 'application/json'
        }

        # Iterate over the list of test cases and send POST requests to the target instance
        for test_case in data['values']:
            # Create the POST request payload for each test case
            oldKey = test_case['key']
            post_tc_payload = {
                "projectKey": targetProjectKey,  # Assuming this is a constant value for all test cases
                "name": test_case['name'],
                "objective": test_case.get('objective', ''),
                "precondition": test_case.get('precondition', ''),
                "estimatedTime": test_case.get('estimatedTime', 0),
                # "componentId": test_case['component']['id'] if 'component' in test_case else None,
                # "priorityName": test_case.get('priorityName', ''),  # Assuming this is a constant value or map it if needed
                # "statusName": test_case.get('statusName', ''),  # Assuming this is a constant value or map it if needed
                # "folderId": test_case['folder']['id'] if 'folder' in test_case else None,
                # "ownerId": test_case.get('owner', {}).get('id', None),
                # "labels": test_case.get('labels', []),
                # "customFields": test_case.get('customFields', {})
            }

            # Send the POST request to the target instance
            post_url = f"{target_base_url}/testcases"
            response = requests.post(post_url, headers=target_headers, data=json.dumps(post_tc_payload))

            # Check if the POST request was successful
            if response.status_code == 201:
                print(f"Successfully created test case: {test_case['name']}")
                response_content = response.json()  # Parse the JSON response content
                NewTcKey = response_content.get('key')  # Extract the 'key' from the response
                print(f"Old Key:{oldKey} New Key: {NewTcKey}")
                new_tc_keys.append(NewTcKey)  # Store the new test case key
                old_tc_keys.append(oldKey)
                print(payload_content)
            else:
                print(f"Failed to create test case: {test_case['name']}. Status code: {response.status_code}, Response: {response.text}")
                
    return old_tc_keys, new_tc_keys  # Return both lists of old and new test case keys

def migrateTestSteps(old_tc_keys, new_tc_keys, source_base_url, source_bearer_token, target_base_url, target_bearer_token):
    source_headers = {
        'Authorization': f'Bearer {source_bearer_token}'
    }
    for old_key, new_key in zip(old_tc_keys, new_tc_keys):
        print(f"Migrating test steps from old test case {old_key} to new test case {new_key}")
        getStepsURL = f'{source_base_url}/testcases/{old_key}/testscript'
        response = requests.get(getStepsURL, headers=source_headers)
        if response.status_code ==200:
            print('Great success')
            print(response.content)
        else:
            print("Steps Get Failure")
            print(response.content)
        # Add logic here to migrate test steps using oldKey and NewTcKey
        # Example: making additional API calls to retrieve steps from oldKey and create them for newKey

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python script.py <source_base_url> <source_bearer_token> <target_base_url> <target_bearer_token>")
        sys.exit(1)

    source_base_url = sys.argv[1]
    source_bearer_token = sys.argv[2]
    target_base_url = sys.argv[3]
    target_bearer_token = sys.argv[4]

    old_tc_keys, new_tc_keys = migrateTC(source_base_url, source_bearer_token, target_base_url, target_bearer_token)
    migrateTestSteps(old_tc_keys, new_tc_keys, source_base_url, source_bearer_token, target_base_url, target_bearer_token)
