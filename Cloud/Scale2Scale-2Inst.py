import requests
import sys
import json
import logging

# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

def migrateStatus(source_base_url, source_bearer_token, sourceProjectKey):
    source_headers = {
        'Authorization': f'Bearer {source_bearer_token}'
    }
    url = f'{source_base_url}/statuses?statusType=TEST_EXECUTION&projectKey={sourceProjectKey}'
    response = requests.get(url, headers=source_headers)
    if response.status_code == 200:
        data = response.json()
        status_kvp = {status['id']: status['name'] for status in data['values']}
        return status_kvp
    else:
        print(f"Failed to retrieve statuses. Status code: {response.status_code}")
        return {}

def migrateTC(source_base_url, source_bearer_token, target_base_url, target_bearer_token, sourceProjectKey, targetProjectKey):
    start_at = 100  # Starting point, make sure this is within the valid range of available test cases
    max_results = 10
    old_to_new_tc_keys = {}

    source_headers = {
        'Authorization': f'Bearer {source_bearer_token}'
    }

    target_headers = {
        'Authorization': f'Bearer {target_bearer_token}',
        'Content-Type': 'application/json'
    }

    while True:
        url = f'{source_base_url}/testcases?startAt={start_at}&maxResults={max_results}&projectKey={sourceProjectKey}'
        response = requests.get(url, headers=source_headers)

        if response.status_code == 200:
            data = response.json()
            total = data['total']  # Get the total number of test cases
            start_at += max_results  # Move to the next batch
     
            if not data['values']:
                print("No more test cases to migrate.")
                break

            for test_case in data['values']:
                oldKey = test_case['key']  # Ensure the ID is used
                
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
                    response_content = response.json()
                    NewTcKey = response_content.get('key')
                    print(f"Successfully created test case from {oldKey} to {NewTcKey}")
                    old_to_new_tc_keys[oldKey] = NewTcKey  # Store the mapping using the ID
                    
                    # Migrate test steps or scripts
                    test_script_url = test_case['testScript']['self']
                    try:
                        migrate_steps_or_scripts(test_script_url, oldKey, NewTcKey, source_headers, target_headers, target_base_url)
                    except Exception as e:
                        logging.error(f"Error migrating steps/scripts for test case {oldKey} -> {NewTcKey}: {str(e)}")
                    
                else:
                    error_message = f"Failed to create test case: {test_case['name']}. Status code: {response.status_code}, Response: {response.text}"
                    print(error_message)
                    logging.error(f"Failed to create test case: {test_case['name']}. Status code: {response.status_code}")
                    logging.error(f"Response content: {response.text}")
            
            # Check if we've reached the end of the available test cases
            if start_at >= total:
                break

        else:
            error_message = f"Failed to retrieve test cases. Status code: {response.status_code}, Response: {response.text}"
            print(error_message)
            logging.error(f"Failed to retrieve test cases. Status code: {response.status_code}")
            logging.error(f"Response content: {response.text}")
            break
    print(old_to_new_tc_keys)
    return old_to_new_tc_keys  # Return the mapping for use in migrate_executions



"""def migrateTC(source_base_url, source_bearer_token, target_base_url, target_bearer_token, sourceProjectKey, targetProjectKey):
    start_at = 106  # Starting point, make sure this is within the valid range of available test cases
    max_results = 1
    old_to_new_tc_keys = {}

    source_headers = {
        'Authorization': f'Bearer {source_bearer_token}'
    }

    target_headers = {
        'Authorization': f'Bearer {target_bearer_token}',
        'Content-Type': 'application/json'
    }

    while True:
        url = f'{source_base_url}/testcases?startAt={start_at}&maxResults={max_results}&projectKey={sourceProjectKey}'
        response = requests.get(url, headers=source_headers)

        if response.status_code == 200:
            data = response.json()
            total = data['total']  # Get the total number of test cases
            start_at += max_results  # Move to the next batch

            if not data['values']:
                print("No more test cases to migrate.")
                break

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
                    response_content = response.json()
                    NewTcKey = response_content.get('key')
                    print(f"Successfully created test case from {oldKey} to {NewTcKey}")
                    old_to_new_tc_keys[oldKey] = NewTcKey  # Store the mapping
                    test_script_url = test_case['testScript']['self']

                    # Migrate test steps or scripts
                    try:
                        migrate_steps_or_scripts(test_script_url, oldKey, NewTcKey, source_headers, target_headers, target_base_url)
                    except Exception as e:
                        logging.error(f"Error migrating steps/scripts for test case {oldKey} -> {NewTcKey}: {str(e)}")
                    
                else:
                    error_message = f"Failed to create test case: {test_case['name']}. Status code: {response.status_code}, Response: {response.text}"
                    print(error_message)
                    logging.error(f"Failed to create test case: {test_case['name']}. Status code: {response.status_code}")
                    logging.error(f"Response content: {response.text}")
            
            # Check if we've reached the end of the available test cases
            if start_at >= total:
                break

        else:
            error_message = f"Failed to retrieve test cases. Status code: {response.status_code}, Response: {response.text}"
            print(error_message)
            logging.error(f"Failed to retrieve test cases. Status code: {response.status_code}")
            logging.error(f"Response content: {response.text}")
            break

    return old_to_new_tc_keys, oldKey, NewTcKey"""

def migrate_steps_or_scripts(test_script_url, old_key, new_key, source_headers, target_headers, target_base_url):
    
    response = requests.get(test_script_url, headers=source_headers)
    
    if response.status_code == 200:
        step_data = response.json()

        if 'values' in step_data and step_data['values']:
            # Submit request to migrate test steps
            items = []
            for step in step_data['values']:
                if 'inline' in step and step['inline']:
                    step_payload = {
                        "inline": {
                            "description": step['inline'].get('description', ''),
                            "testData": step['inline'].get('testData', ''),
                            "expectedResult": step['inline'].get('expectedResult', ''),
                        }
                    }
                    items.append(step_payload)
                else:
                    logging.error(f"Missing 'inline' key in step: {step}")
                    print(f"Error: Missing 'inline' key in step for test case {old_key}")

            if items:
                getStepsPayload = {
                    "mode": "APPEND",
                    "items": items
                }
                post_steps_url = f"{target_base_url}/testcases/{new_key}/teststeps"
                response = requests.post(post_steps_url, headers=target_headers, data=json.dumps(getStepsPayload))

                if response.status_code == 201:
                    print(f"Successfully migrated steps from {old_key} to {new_key}")
                else:
                    error_message = f"Failed to migrate steps to test case: {new_key}. Status code: {response.status_code}, Response: {response.text}"
                    print(error_message)
                    logging.error(f"Failed to migrate steps to test case: {new_key}. Status code: {response.status_code}")
                    logging.error(f"Response content: {response.text}")

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
                error_message = f"Failed to migrate script to test case: {new_key}. Status code: {response.status_code}, Response: {response.text}"
                print(error_message)
                logging.error(f"Failed to migrate script to test case: {new_key}. Status code: {response.status_code}")
                logging.error(f"Response content: {response.text}")

    else:
        error_message = "Failed to retrieve test steps/scripts."
        print(error_message)
        logging.error(f"{error_message} Status code: {response.status_code}")
        logging.error(f"Response content: {response.content.decode('utf-8')}")

def migrateCycles(source_base_url, source_bearer_token, target_base_url, target_bearer_token, sourceProjectKey, targetProjectKey, old_to_new_tc_keys, status_kvp):
    start_at = 60  # Starting point, adjust as needed
    max_results = 10

    source_headers = {
        'Authorization': f'Bearer {source_bearer_token}'
    }

    target_headers = {
        'Authorization': f'Bearer {target_bearer_token}',
        'Content-Type': 'application/json'
    }

    while True:
        url = f'{source_base_url}/testcycles?startAt={start_at}&maxResults={max_results}&projectKey={sourceProjectKey}'
        response = requests.get(url, headers=source_headers)
        
        if response.status_code == 200:
            try:
                data = response.json()  # Convert the response content to a JSON object
                #print(data)
                
                # Iterate over all cycles in the current response
                for cycle in data['values']:
                    name = cycle.get('name')
                    description = cycle.get('description')
                    planned_start_date = cycle.get('plannedStartDate')
                    planned_end_date = cycle.get('plannedEndDate')
                    oldCycleKey = cycle.get('key')

                    new_payload = {
                        "projectKey": targetProjectKey,
                        "name": name,
                        "description": description,
                        "plannedStartDate": planned_start_date,
                        "plannedEndDate": planned_end_date
                    }
                    post_url = f"{target_base_url}/testcycles"  # Correct URL for creating a new cycle
                    response = requests.post(post_url, headers=target_headers, json=new_payload)
                    
                    if response.status_code == 201:
                        print(f"Successfully migrated Test Cycle {name}")
                        response_content = response.json()
                        newCycleKey = response_content.get('key')  # Get the new cycle key
                        
                        # Migrate test executions for this cycle
                        try:
                            migrate_executions(oldCycleKey, newCycleKey, source_headers, target_headers, target_base_url, old_to_new_tc_keys, targetProjectKey, status_kvp)
                        except Exception as e:
                            logging.error(f"Error migrating executions for cycle {oldCycleKey} -> {newCycleKey}: {str(e)}")
                    else:
                        print(f"Error posting cycle {name}. Status code: {response.status_code}")
                        logging.error(f"Failed to migrate test cycle: {name}. Status code: {response.status_code}")
                        logging.error(f"Response content: {response.text}")

                # Check if there are more cycles to fetch based on 'isLast'
                if data.get('isLast', True):  # If isLast is True, we've fetched all cycles
                    print("All test cycles migrated.")
                    break
                else:
                    # Increment start_at to fetch the next batch of cycles
                    start_at += max_results

            except json.JSONDecodeError as e:
                # Handle the case where the response content isn't JSON serializable
                logging.error(f"Failed to decode JSON response: {str(e)}")
                logging.error(f"Response content: {response.content.decode('utf-8')}")
                print(f"Error: Failed to decode JSON response.")
                break  # Stop the loop if there's a decoding error
        else:
            error_message = f"Failed to retrieve test cycles. Status code: {response.status_code}, Response: {response.text}"
            print(error_message)
            logging.error(f"Failed to retrieve test cycles. Status code: {response.status_code}")
            logging.error(f"Response content: {response.text}")
            break  # Exit the loop if there's an error retrieving cycles


def migrate_executions(oldCycleKey, newCycleKey, source_headers, target_headers, target_base_url, old_to_new_tc_keys, targetProjectKey, status_kvp):
    url = f'{target_base_url}/testexecutions?testCycle={oldCycleKey}'
    
    response = requests.get(url, headers=source_headers)
    
    if response.status_code == 200:
        execution_data = response.json()
        for execution in execution_data['values']:
            #oldTestCaseKey = execution.get('testCaseKey')  # Get the old test case key from execution
            
            new_tc_keys_list = list(old_to_new_tc_keys.values())

            
                
        for newTestCaseKey in new_tc_keys_list:
            status_id = execution.get('testExecutionStatus', {}).get('id')
            status_name = status_kvp.get(status_id, 'Unknown Status')

            new_execution_payload = {
                "projectKey": targetProjectKey,
                "testCaseKey": newTestCaseKey,
                "testCycleKey": newCycleKey,
                "statusName": status_name,
            }

            print(f"Starting to migrate executions for new test case {newTestCaseKey}")
            post_url = f"{target_base_url}/testexecutions"
            response = requests.post(post_url, headers=target_headers, json=new_execution_payload)
            
            if response.status_code == 201:
                print(f"Successfully migrated execution for test case {newTestCaseKey}")
            else:
                print(f"Error posting execution for test case {newTestCaseKey}: {response.status_code}")
                logging.error(f"Failed to migrate execution for test case {newTestCaseKey}. Status code: {response.status_code}")
                logging.error(f"Response content: {response.text}")
    else:
        error_message = f"Failed to retrieve executions for test cycle {oldCycleKey}. Status code: {response.status_code}, Response: {response.text}"
        print(error_message)
        logging.error(error_message)
        logging.error(f"Response content: {response.text}")



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


    # Capture status KVP
    status_kvp = migrateStatus(source_base_url, source_bearer_token, sourceProjectKey)

    # Migrate test cases and store the old-to-new keys mapping
    old_to_new_tc_keys = migrateTC(source_base_url, source_bearer_token, target_base_url, target_bearer_token, sourceProjectKey, targetProjectKey)

    # Migrate cycles and executions, passing the status KVP
    migrateCycles(source_base_url, source_bearer_token, target_base_url, target_bearer_token, sourceProjectKey, targetProjectKey, old_to_new_tc_keys, status_kvp)
