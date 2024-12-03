import requests
from requests.auth import HTTPBasicAuth
import sys
import re
import json
import os

# In order to run the script, configure the fields below. Then run the python command with version 2.7 as the interpreter.
# EX: python2.7 Custom-Status-Priority-Fields2.7.py <projectKey> <projectID>      
# EX: python2.7 Custom-Status-Priority-Fields2.7.py ZULU 10169

## The migration of the test case status, test case priority, and custom fields are all seperate functions. That are executed in sequence in this script
# To migrate statuses or priorities, we need to supply the project key as input 
# To migrate custom feilds, we need to supply the project id as input.  
# When we migrate both of these via the script - for continuity, migrate the a single projects project key and project ID.

#### REPLACE ME WITH JIRA USER EMAIL #######   Requried for JWT and Custom Field functions
username = "<Jira User Email>"

#### REPLACE ME WITH JIRA API TOKEN #######    Requried for JWT and Custom Field functions
jira_api_token = "<Jira API Token>"

#### REPLACE <your-jira-instance> with the Jira instance #######       Requried for JWT and Custom Field functions
jwt_url = "https://<your-jira-instance>.atlassian.net/plugins/servlet/ac/com.kanoah.test-manager/main-project-page"

#### REPLACE ME WITH ZEPHYR SCALE BEARER TOKEN #######          Requried for Priorty and Status functions
bearer_token = "<>"

# REPLACE ME WITH NEW ZEPHYR SCALE TEST CASE STATUSES. Draft, Deprecated, and Approved are default values.       Requried for Priorty and Status functions
otherStatuses = set(["Review"])

# REPLACE ME WITH NEW ZEPHYR SCALE TEST PRIORITIES. Low, Medium, and High are default values.         Requried for Priorty and Status functions
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
            elif response.status_code == 400 and "A priority with this name already exists" in response.json().get("message", ""):
                print("Conflict: Priority '{}' already exists in project '{}'.".format(name, projectkey))
            else:
                print("Failed to create priority '{}': {}".format(name, response.status_code))
                print(response.content.decode())
    except requests.exceptions.RequestException as e:
        print("Request failed: {}".format(e))

def get_jwt():
    """
    Fetches the contextJwt from the API endpoint by parsing the response.

    Returns:
        str: The contextJwt token if successful, None otherwise.
    """
    global jwt_url, username, jira_api_token  # Declare these as global
    url = jwt_url
    username = username
    jira_api_token = jira_api_token

    try:
        response = requests.post(
            url,
            auth=HTTPBasicAuth(username, jira_api_token)
        )

        # Check if the response is successful
        if response.status_code == 200:
            # Parse the contextJwt using regex
            match = re.search(r'"contextJwt":"(.*?)"', response.text)
            if match:
                context_jwt = match.group(1)
                print("Retrieved contextJwt")
                return context_jwt
            else:
                print("contextJwt not found in the response.")
                print(response.content)
                return None
        else:
            print("Failed to fetch JWT. Status Code: {}".format(response.status_code))
            print("Response Content: {}".format(response.text))
            return None
    except requests.exceptions.RequestException as e:
        print("An error occurred while fetching JWT: {}".format(e))
        return None

def create_custom_field(context_jwt, project_id):
    """
    Creates custom fields in the specified project using the JWT token and payload from a JSON file.

    Args:
        context_jwt (str): The JWT token for authentication.
        project_id (int): The ID of the Jira project.

    Returns:
        list: A list of response JSONs if any requests fail.
        None: If all requests are successful.
    """
    url = "https://app.tm4j.smartbear.com/backend/rest/tests/2.0/customfield/testcase"
    
    headers = {
        "Authorization": "JWT {}".format(context_jwt),
        "Content-Type": "application/json",
        "Jira-Project-Id": str(project_id)
    }

    # Read payload from custom_fields.json
    json_file_path = os.path.join(os.path.dirname(__file__), 'custom_fields.json')
    
    try:
        with open(json_file_path, 'r') as json_file:
            payload = json.load(json_file)
            if not isinstance(payload, list):
                raise ValueError("Expected a list of custom fields in the JSON file.")
    except IOError:
        print("Error: The file custom_fields.json was not found in {}.".format(json_file_path))
        return None
    except ValueError as e:
        print("Error: {}".format(e))
        return None

    failed_responses = []

    for field in payload:
        if isinstance(field, dict):  # Ensure it's an object
            field["projectId"] = str(project_id)  # Update projectId dynamically
            
            try:
                response = requests.post(url, headers=headers, json=field)
                
                if response.status_code == 200:
                    # Minimal logging for success
                    print("Custom field '{}' created successfully.".format(field.get("name", "Unnamed")))
                elif response.status_code == 409:
                    # Log conflict but do not consider it a failure
                    print("Conflict: Custom field '{}' already exists.".format(field.get("name", "Unnamed")))
                else:
                    # Log failure details and append to failed responses
                    print("Failed to create custom field '{}': Status Code {}".format(
                        field.get("name", "Unnamed"), response.status_code))
                    print("Response Body: {}".format(response.text))
                    failed_responses.append({
                        "field": field,
                        "status_code": response.status_code,
                        "response": response.text
                    })
            except requests.exceptions.RequestException as e:
                print("An error occurred while creating the custom field '{}': {}".format(
                    field.get("name", "Unnamed"), str(e)))
                failed_responses.append({"field": field, "error": str(e)})
        else:
            print("Skipping non-dictionary item in JSON payload: {}".format(field))

    return failed_responses if failed_responses else None


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python2 Custom-Status-Priority-Fields.py <projectKey1> <project_id>")
        sys.exit(1)

    print("Received arguments:", sys.argv)  # Debugging line

    # Treat the first argument as the single project key
    projectkey = sys.argv[1]
    # Treat the second argument as the project ID
    project_id = sys.argv[2]

    print("Processing project key: '{}'".format(projectkey))
    test_case_status(projectkey)
    test_case_priority(projectkey)

    # Fetch the JWT token
    context_jwt = get_jwt()
    if context_jwt:
        create_custom_field(context_jwt, project_id)
    else:
        print("Failed to retrieve JWT token. Exiting.")

    print("Finished processing project key '{}' and project ID '{}'.".format(projectkey, project_id))