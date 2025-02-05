import requests
import json
import logging
import sys
import urllib3

# Disable SSL warnings (since verify=False is used)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

def migrateStatus(source_base_url, source_bearer_token, sourceProjectKey):
    source_headers = {
        'Authorization': f'Bearer {source_bearer_token}'
    }
    url = f'{source_base_url}/statuses?statusType=TEST_EXECUTION&projectKey={sourceProjectKey}'
    
    try:
        response = requests.get(url, headers=source_headers, verify=False)  # Bypass SSL
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        data = response.json()
        return {status['id']: status['name'] for status in data.get('values', [])}
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve statuses: {e}")
        print(f"Error: {e}")
        return {}

def migrateTC(source_base_url, source_bearer_token, target_base_url, target_bearer_token, sourceProjectKey, targetProjectKey):
    start_at = 0  # Make sure this is within the valid range of available test cases
    max_results = 100
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
        
        try:
            response = requests.get(url, headers=source_headers, verify=False)  # Bypass SSL
            response.raise_for_status()  # Raise an error if the request fails
            data = response.json()
            total = data.get('total', 0)

            if not data.get('values', []):
                print("No more test cases to migrate.")
                break

            start_at += max_results  # Move to the next batch

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
                
                try:
                    post_response = requests.post(post_url, headers=target_headers, json=post_tc_payload, verify=False)  # Bypass SSL
                    post_response.raise_for_status()
                    new_tc_data = post_response.json()
                    newKey = new_tc_data.get('key', None)

                    if newKey:
                        old_to_new_tc_keys[oldKey] = newKey
                except requests.exceptions.RequestException as e:
                    logging.error(f"Failed to migrate test case {oldKey}: {e}")
                    print(f"Error migrating test case {oldKey}: {e}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to retrieve test cases: {e}")
            print(f"Error: {e}")
            break

    return old_to_new_tc_keys

# Ensure required arguments are provided
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

    print("Migrating statuses...")
    statuses = migrateStatus(source_base_url, source_bearer_token, sourceProjectKey)
    print("Statuses migrated:", statuses)

    print("Migrating test cases...")
    tc_mappings = migrateTC(source_base_url, source_bearer_token, target_base_url, target_bearer_token, sourceProjectKey, targetProjectKey)
    print("Test case mappings:", tc_mappings)


