import requests
import json
import logging
import sys
import urllib3

# Disable SSL warnings (since verify=False is used)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# General execution logging (app.log)
app_logger = logging.getLogger("app_logger")
app_logger.setLevel(logging.DEBUG)
app_handler = logging.FileHandler("app.log")
app_handler.setFormatter(log_formatter)
app_logger.addHandler(app_handler)

# Error logging (error.log)
error_logger = logging.getLogger("error_logger")
error_logger.setLevel(logging.ERROR)
error_handler = logging.FileHandler("error.log")
error_handler.setFormatter(log_formatter)
error_logger.addHandler(error_handler)


def migrateTEStatus(source_base_url, source_bearer_token, sourceProjectKey):
    source_headers = {'Authorization': f'Bearer {source_bearer_token}'}
    url = f'{source_base_url}/statuses?statusType=TEST_EXECUTION&projectKey={sourceProjectKey}'

    app_logger.info(f"Fetching execution statuses from {url}")

    try:
        response = requests.get(url, headers=source_headers, verify=False)
        response.raise_for_status()
        data = response.json()
        status_count = len(data.get('values', []))
        app_logger.info(f"Successfully fetched {status_count} execution statuses.")
        return {status['id']: status['name'] for status in data.get('values', [])}
    except requests.exceptions.RequestException as e:
        error_logger.error(f"Failed to retrieve statuses: {e}")
        return {}  

def migrateTCStatus(source_base_url, source_bearer_token, sourceProjectKey):
    source_headers = {'Authorization': f'Bearer {source_bearer_token}'}
    url = f'{source_base_url}/statuses?statusType=TEST_CASE&projectKey={sourceProjectKey}'

    print(f"Fetching test case statuses from {url}")

    try:
        response = requests.get(url, headers=source_headers, verify=False)
        response.raise_for_status()
        data = response.json()
        status_count = len(data.get('values', []))
        print(f"Successfully fetched {status_count} test case statuses.")
        return {status['id']: status['name'] for status in data.get('values', [])}
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve test case statuses: {e}")
        return {}

def migrateTC(source_base_url, source_bearer_token, target_base_url, target_bearer_token, sourceProjectKey, targetProjectKey, status_mapping):
    """
    Fetches test cases from the source project and migrates them to the target project.
    """
    start_at = 0  
    max_results = 100  
    old_to_new_tc_keys = {}

    source_headers = {'Authorization': f'Bearer {source_bearer_token}'}
    target_headers = {'Authorization': f'Bearer {target_bearer_token}', 'Content-Type': 'application/json'}

    while True:
        url = f'{source_base_url}/testcases?startAt={start_at}&maxResults={max_results}&projectKey={sourceProjectKey}'
        
        try:
            response = requests.get(url, headers=source_headers, verify=False)
            response.raise_for_status()
            data = response.json()

            if not data.get('values', []):
                app_logger.info("No more test cases to migrate.")
                break

            start_at += max_results  

            for test_case in data['values']:
                oldKey = test_case['key']
                
                # Fetch Status Name from Mapping (Default to "Not Executed" if not found)
                status_id = test_case.get("status", {}).get("id")
                status_name = status_mapping.get(status_id, "Not Executed")

                # Ensure folder ID is correctly retrieved
                #folder_id = test_case.get("folder", {}).get("id", None)

                post_tc_payload = {
                    "projectKey": targetProjectKey,
                    "name": test_case['name'],
                    "objective": test_case.get('objective', ''),
                    #"folderId": folder_id,
                    "precondition": test_case.get('precondition', ''),
                    "estimatedTime": test_case.get('estimatedTime', 0),
                    "statusName": status_name 
                }

                post_url = f"{target_base_url}/testcases"
                
                try:
                    post_response = requests.post(post_url, headers=target_headers, json=post_tc_payload, verify=False)
                    post_response.raise_for_status()
                    new_tc_data = post_response.json()
                    newKey = new_tc_data.get('key')

                    if newKey:
                        old_to_new_tc_keys[oldKey] = newKey
                        app_logger.info(f"Migrated test case {oldKey} → {newKey}")
                except requests.exceptions.RequestException as e:
                    error_logger.error(f"Failed to migrate test case {oldKey}: {e}")
                    error_logger.error(f"Response: {post_response.text}")
                    error_logger.error(f"Payload: {post_tc_payload}")

        except requests.exceptions.RequestException as e:
            error_logger.error(f"Failed to retrieve test cases: {e}")
            break

    return old_to_new_tc_keys

def fetchTestCycles(source_base_url, source_bearer_token, sourceProjectKey, start_at=0, max_results=50):
    """
    Fetches test cycles from the source project with pagination support.
    """
    headers = {"Authorization": f"Bearer {source_bearer_token}", "Content-Type": "application/json"}
    cycles_endpoint = f"{source_base_url}/testcycles?startAt={start_at}&maxResults={max_results}&projectKey={sourceProjectKey}"
    
    response = requests.get(cycles_endpoint, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch test cycles: {response.status_code}")
        return None

    return response.json()

def migrateTestCycle(target_base_url, target_bearer_token, cycle, targetProjectKey, old_to_new_tc_keys, status_kvp, source_base_url, source_bearer_token, cycle_mapping):
    old_cycle_key = cycle["key"]
    new_cycle_payload = {
        "name": cycle["name"],
        "projectKey": targetProjectKey,
        "plannedStartDate": cycle.get("plannedStartDate"),
        "plannedEndDate": cycle.get("plannedEndDate"),
        "status": cycle["status"]["id"]
    }

    create_cycle_endpoint = f"{target_base_url}/testcycles"
    app_logger.info(f"Creating test cycle {old_cycle_key}")

    try:
        response = requests.post(create_cycle_endpoint, json=new_cycle_payload, headers={"Authorization": f"Bearer {target_bearer_token}", "Content-Type": "application/json"})
        response.raise_for_status()
        new_cycle_key = response.json().get("key")
        app_logger.info(f"Test cycle migrated: {old_cycle_key} → {new_cycle_key}")

        migrate_executions(source_base_url, source_bearer_token, target_base_url, target_bearer_token,
                           old_cycle_key, new_cycle_key, sourceProjectKey, old_to_new_tc_keys, status_kvp, cycle_mapping)
    except requests.exceptions.RequestException as e:
        error_logger.error(f"Failed to migrate cycle {old_cycle_key}: {e}")

def migrateCycles(source_base_url, source_bearer_token, target_base_url, target_bearer_token, sourceProjectKey, targetProjectKey, old_to_new_tc_keys, status_kvp):
    """
    Migrates all test cycles from the source project to the target project.
    """
    print("Fetching cycle mapping before migration...")
    cycle_mapping = get_cycle_mapping(source_base_url, source_bearer_token, sourceProjectKey)

    start_at = 0
    max_results = 50  # Adjust if needed

    while True:
        cycles_data = fetchTestCycles(source_base_url, source_bearer_token, sourceProjectKey, start_at, max_results)
        
        if not cycles_data or "values" not in cycles_data or len(cycles_data["values"]) == 0:
            break  # No more cycles to process

        for cycle in cycles_data["values"]:
            migrateTestCycle(target_base_url, target_bearer_token, cycle, targetProjectKey, old_to_new_tc_keys, status_kvp, source_base_url, source_bearer_token, cycle_mapping)

        start_at += max_results  # Move to the next batch

    print("Test Cycles migration completed!")

def get_cycle_mapping(source_base_url, source_bearer_token, sourceProjectKey):
    """Fetch all test cycles and create a mapping of cycle keys to cycle IDs."""
    headers = {"Authorization": f"Bearer {source_bearer_token}", "Content-Type": "application/json"}
    cycles_endpoint = f"{source_base_url}/testcycles?projectKey={sourceProjectKey}&startAt=0&maxResults=50"
    
    print("Requesting test cycles from", cycles_endpoint)
    
    response = requests.get(cycles_endpoint, headers=headers)
    
    if response.status_code != 200:
        print("Failed to fetch test cycles:", response.status_code, response.text)
        return {}

    cycles_data = response.json().get("values", [])
    
    cycle_mapping = {cycle["key"]: cycle["id"] for cycle in cycles_data}
    
    print("Cycle mapping created:", cycle_mapping)
    return cycle_mapping

def fetch_executions_from_cycle(source_base_url, source_bearer_token, sourceProjectKey, cycle_key, cycle_mapping):
    headers = {"Authorization": f"Bearer {source_bearer_token}", "Content-Type": "application/json"}
    
    if cycle_key not in cycle_mapping:
        error_logger.error(f"Cycle key {cycle_key} not found in mapping")
        return []

    cycle_id = cycle_mapping[cycle_key]
    executions_endpoint = f"{source_base_url}/testexecutions?projectKey={sourceProjectKey}&startAt=0&maxResults=50"
    
    app_logger.info(f"Fetching executions for cycle {cycle_key}")

    try:
        response = requests.get(executions_endpoint, headers=headers)
        response.raise_for_status()
        executions_data = response.json().get("values", [])

        filtered_executions = [exec for exec in executions_data if exec.get("testCycle", {}).get("id") == cycle_id]
        app_logger.info(f"Executions found for cycle {cycle_key}: {len(filtered_executions)}")
        return filtered_executions
    except requests.exceptions.RequestException as e:
        error_logger.error(f"Failed to fetch executions for cycle {cycle_key}: {e}")
        return []

def post_executions_to_cycle(target_base_url, target_bearer_token, new_cycle_key, targetProjectKey, executions, old_to_new_tc_keys, status_kvp):
    print("Starting to post executions to cycle", new_cycle_key)

    headers = {"Authorization": f"Bearer {target_bearer_token}", "Content-Type": "application/json"}
    posted_count = 0

    for execution in executions:
        test_case_url = execution.get("testCase", {}).get("self", "")

        if not test_case_url or "/testcases/" not in test_case_url:
            print("Skipping execution", execution.get("key", "UNKNOWN"), "due to missing test case key")
            continue

        old_test_case_key = test_case_url.split("/testcases/")[1].split("/")[0]

        if old_test_case_key in old_to_new_tc_keys:
            new_test_case_key = old_to_new_tc_keys[old_test_case_key]

            new_execution_payload = {
                "projectKey": targetProjectKey,
                "testCaseKey": new_test_case_key,
                "testCycleKey": new_cycle_key,
                "statusName": status_kvp.get(execution["testExecutionStatus"]["id"], "Not Executed"),
                "actualEndDate": execution.get("actualEndDate"),
                "estimatedTime": execution.get("estimatedTime"),
                "executionTime": execution.get("executionTime"),
                "executedById": execution.get("executedById"),
                "assignedToId": execution.get("assignedToId"),
                "comment": execution.get("comment"),
                "automated": execution.get("automated"),
                "environment": execution.get("environment"),
            }

            print("Posting execution", execution["key"], "to new test case", new_test_case_key, "in cycle", new_cycle_key)
            create_execution_endpoint = f"{target_base_url}/testexecutions"
            response = requests.post(create_execution_endpoint, json=new_execution_payload, headers=headers)

            if response.status_code == 201:
                print("Successfully migrated execution", execution["key"], "to test case", new_test_case_key)
                posted_count += 1
            else:
                print("Failed to migrate execution", execution["key"], "Status Code:", response.status_code)
                print("Response Text:", response.text)
        else:
            print("Skipping execution", execution["key"], "as no mapping found for test case", old_test_case_key)

    print("Total executions posted for cycle", new_cycle_key, ":", posted_count)

def migrate_executions(source_base_url, source_bearer_token, target_base_url, target_bearer_token, old_cycle_key, new_cycle_key, sourceProjectKey, old_to_new_tc_keys, status_kvp, cycle_mapping):    
    print("Migrating executions from cycle", old_cycle_key, "to", new_cycle_key)

    executions = fetch_executions_from_cycle(source_base_url, source_bearer_token, sourceProjectKey, old_cycle_key, cycle_mapping)

    if not executions:
        print("No executions found for cycle", old_cycle_key, "Skipping execution migration.")
        return

    post_executions_to_cycle(target_base_url, target_bearer_token, new_cycle_key, targetProjectKey, executions, old_to_new_tc_keys, status_kvp)

# Main execution flow
if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python Scale2Scale-2Inst3.py <source_bearer_token> <target_bearer_token> <sourceProjectKey> <targetProjectKey>")
        sys.exit(1)

    # Read input values from command-line arguments
    source_base_url = "https://api.zephyrscale.smartbear.com/v2"
    target_base_url = source_base_url
    source_bearer_token = sys.argv[1]
    target_bearer_token = sys.argv[2]
    sourceProjectKey = sys.argv[3]
    targetProjectKey = sys.argv[4]

    print("Migrating execution statuses...")
    status_kvp = migrateTEStatus(source_base_url, source_bearer_token, sourceProjectKey)
    print("Execution statuses migrated:", status_kvp)

    print("Fetching test case statuses...")
    status_mapping = migrateTCStatus(source_base_url, source_bearer_token, sourceProjectKey)  
    print("Test case statuses fetched:", status_mapping)

    print("Migrating test cases...")
    old_to_new_tc_keys = migrateTC(source_base_url, source_bearer_token, target_base_url, target_bearer_token, sourceProjectKey, targetProjectKey, status_mapping) 
    print("Test cases migrated:", old_to_new_tc_keys)

    print("Migrating Cycles and Executions....")
    migrateCycles(source_base_url, source_bearer_token, target_base_url, target_bearer_token, sourceProjectKey, targetProjectKey, old_to_new_tc_keys, status_kvp)
