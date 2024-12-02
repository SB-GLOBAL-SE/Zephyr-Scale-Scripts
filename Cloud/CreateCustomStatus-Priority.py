
import requests
import sys
import json


# In order to run the script, configure the bearer_token, otherStatuses, and otherPriorities below. Then run the python command with version 2.7 as the interpreter.
# EX: python2.7 CreateCustomStatuses.py <projectKeys to migrate (1 or multiple)>
# EX: python2.7 CreateCustomStatuses.py ZULU
# EX: python2.7 CreateCustomStatuses.py ZULU APPS OPS


#### REPLACE ME WITH ZEPHYR SCALE BEARER TOKEN #######
bearer_token = "<Replace with Zephyr Scale Bearer Token>"

# REPLACE ME WITH NEW ZEPHYR SCALE TEST CASE STATUSES. Draft, Deprecated, and Approved are default values.
otherStatuses = set(["Review", "Review1", "Review2"])

# Replace this with new Zephyr Scale priority statuses.
otherPriorities = set(["Critical"])

# Global value, do NOT change!
base_url = "https://api.zephyrscale.smartbear.com/v2"


def test_case_status(projectkey):
    """
    Create test case statuses for the specified project.
    """
    url = '{}/statuses'.format(base_url)

    headers = {
        'Authorization': 'Bearer {}'.format(bearer_token),
        'Content-Type': 'application/json'
    }

    try:
        for name in otherStatuses:
            # Update the status payload for each status name
            status_payload = {
                "projectKey": projectkey,
                "name": name,
                "type": "TEST_CASE",
                "color": "#0052cc"
            }

            # POST request to create the status
            response = requests.post(url, headers=headers, data=json.dumps(status_payload))

            if response.status_code == 201:
                response_data = response.json()
                print("Successfully created Status '{}': {}".format(name, projectkey))
            elif response.status_code == 400 and "A status of this type with this name already exists" in response.json().get("message", ""):
                print("Conflict: Status '{}' already exists in project '{}'.".format(name, projectkey))
            else:
                print("Failed to create status '{}': {}".format(name, response.status_code))
                print(response.content.decode())
    except requests.exceptions.RequestException as e:
        print("Request failed: {}".format(e))

def test_case_priority(projectkey):
    """
    Create test case priorities for the specified project.
    """
    url = '{}/priorities'.format(base_url)

    headers = {
        'Authorization': 'Bearer {}'.format(bearer_token),
        'Content-Type': 'application/json'
    }

    try:
        for name in otherPriorities:
            # Update the priority payload for each priority name
            priority_payload = {
                "projectKey": projectkey,
                "name": name,
                "color": "#EC3536"
            }

            # POST request to create the priority
            response = requests.post(url, headers=headers, data=json.dumps(priority_payload))

            if response.status_code == 201:
                response_data = response.json()
                print("Successfully created Priority '{}': {}".format(name, projectkey))
            elif response.status_code == 400 and "A Priority with this name already exists" in response.json().get("message", ""):
                print("Conflict: Priority '{}' already exists in project '{}'.".format(name, projectkey))
            else:
                print("Failed to create priority '{}': {}".format(name, response.status_code))
                print(response.content.decode())
    except requests.exceptions.RequestException as e:
        print("Request failed: {}".format(e))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python2.7 python.py <projectKey1> <projectKey2> ...")
        sys.exit(1)

    # Loop through all provided project keys
    for projectkey in sys.argv[1:]:
        print("Processing project key: {}".format(projectkey))
        test_case_status(projectkey)
        test_case_priority(projectkey)
