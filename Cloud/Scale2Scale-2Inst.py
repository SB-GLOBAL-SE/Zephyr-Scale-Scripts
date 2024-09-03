import requests
import io
import sys
import json

def migrateTC(source_base_url, source_bearer_token, target_base_url, target_bearer_token, sourceProjectKey, targetProjectKey):

    url = f'{source_base_url}/testcases?startAt=1&maxResults=2&projectKey={sourceProjectKey}'

    source_headers = {
        'Authorization': f'Bearer {source_bearer_token}'
    }

    response = requests.get(url, headers=source_headers)
    old_tc_keys = []
    new_tc_keys = []

    if response.status_code == 200:
        payload_io = io.StringIO(response.text)
        payload_content = payload_io.getvalue()
        
        data = json.loads(payload_content)
        
        target_headers = {
            'Authorization': f'Bearer {target_bearer_token}',
            'Content-Type': 'application/json'
        }

        for test_case in data['values']:
            oldKey = test_case['key']
            post_tc_payload = {
                "projectKey": targetProjectKey,
                "name": test_case['name'],
                "objective": test_case.get('objective', ''),
                "precondition": test_case.get('precondition', ''),
                "estimatedTime": test_case.get('estimatedTime', 0),
            }

            post_url = f"{target_base_url}/testcases"
            response = requests.post(post_url, headers=target_headers, data=json.dumps(post_tc_payload))

            if response.status_code == 201:
                print(f"Successfully created test case: {test_case['name']}")
                response_content = response.json()
                NewTcKey = response_content.get('key')
                print(f"Old Key:{oldKey} New Key: {NewTcKey}")
                new_tc_keys.append(NewTcKey)
                old_tc_keys.append(oldKey)
                test_script_url = test_case['testScript']['self']

                # Migrate test steps or scripts
                migrate_steps_or_scripts(test_script_url, oldKey, NewTcKey, source_headers, target_headers, target_base_url)
                
            else:
                print(f"Failed to create test case: {test_case['name']}. Status code: {response.status_code}, Response: {response.text}")
    else:
        print(f"Failed to retrieve test cases. Status code: {response.status_code}, Response: {response.text}")
                
    return old_tc_keys, new_tc_keys

def migrate_steps_or_scripts(test_script_url, old_key, new_key, source_headers, target_headers, target_base_url):
    print(f"Migrating test steps/scripts from old test case {old_key} to new test case {new_key}")
    
    response = requests.get(test_script_url, headers=source_headers)
    
    if response.status_code == 200:
        step_data = response.json()

        if 'values' in step_data and step_data['values']:
            # Submit request to migrate test steps
            items = []
            for step in step_data['values']:
                step_payload = {
                    "inline": {
                        "description": step['inline']['description'],
                        "testData": step['inline']['testData'],
                        "expectedResult": step['inline']['expectedResult'],
                    }
                }
                items.append(step_payload)

            getStepsPayload = {
                "mode": "APPEND",
                "items": items
            }
            post_steps_url = f"{target_base_url}/testcases/{new_key}/teststeps"
            response = requests.post(post_steps_url, headers=target_headers, data=json.dumps(getStepsPayload))

            if response.status_code == 201:
                print(f"Successfully migrated steps to new test case: {new_key}")
            else:
                print(f"Failed to migrate steps to test case: {new_key}. Status code: {response.status_code}, Response: {response.text}")

        else:
            # Handle the case where there are no values and instead the structure is direct
            script_payload = {
                "type": step_data.get("type", "plain"),
                "text": step_data.get("text", ""),
                "id": step_data.get("id")
            }
            post_script_url = f"{target_base_url}/testcases/{new_key}/testscript"
            response = requests.post(post_script_url, headers=target_headers, data=json.dumps(script_payload))

            if response.status_code == 201:
                print(f"Successfully migrated script to new test case: {new_key}")
            else:
                print(f"Failed to migrate script to test case: {new_key}. Status code: {response.status_code}, Response: {response.text}")

    else:
        print("Failed to retrieve test steps/scripts")
        print(response.content)

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python script.py <source_base_url> <source_bearer_token> <target_base_url> <target_bearer_token> <sourceProjectKey> <targetProjectKey>")
        sys.exit(1)

    source_base_url = sys.argv[1]
    source_bearer_token = sys.argv[2]
    target_bearer_token = sys.argv[3]
    sourceProjectKey = sys.argv[4]
    targetProjectKey = sys.argv[5]

    target_base_url = source_base_url

    old_tc_keys, new_tc_keys = migrateTC(source_base_url, source_bearer_token, target_base_url, target_bearer_token, sourceProjectKey, targetProjectKey)
