import requests
from requests.auth import HTTPBasicAuth
import sys
import re
import json
import os

# In order to run the script, configure the fields below. Then run the python command with version 2.7 as the interpreter.
# EX: python2.7 CreateTCVersion2.7.py <projectID> 
# EX: python2.7 CreateTCVersion2.7.py 10169

#### REPLACE ME WITH JIRA USER EMAIL #######   Requried 
username = "<Jira User Email>"

#### REPLACE ME WITH JIRA API TOKEN #######    Requried 
jira_api_token = "<Jira API Token>"

#### REPLACE <your-jira-instance> with the Jira instance #######       Requried 
jwt_url = "https://<your-jira-instance>.atlassian.net/plugins/servlet/ac/com.kanoah.test-manager/main-project-page"


### REPLACE <test_case_id> with the Test Case ID you wish to update ###### Required   
test_case_id = <test_case_id>

# Global value, do NOT change!
base_url = "https://api.zephyrscale.smartbear.com/v2"

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

def create_version(context_jwt, project_id):
    """
    Creates a new test case version in the specified project using the JWT token.

    Args:
        context_jwt (str): The JWT token for authentication.
        project_id (int): The ID of the Jira project.

    Returns:
        None: If the request is successful.
        dict: If the request fails, returns a dictionary with status code and response text.
    """


    url = "https://app.tm4j.smartbear.com/backend/rest/tests/2.0/testcase/{}/newversion".format(test_case_id)
    
    headers = {
        "Authorization": "JWT {}".format(context_jwt),
        "Content-Type": "application/json",
        "Jira-Project-Id": str(project_id)
    }

    try:
        response = requests.post(url, headers=headers, json={})  # No payload required

        if response.status_code == 200:
            print("New test case version created successfully.")
        elif response.status_code == 409:
            print("Conflict: A new version already exists for the test case.")
        else:
            print("Failed to create new test case version: Status Code {}".format(response.status_code))
            print("Response Body: {}".format(response.text))
            return {
                "status_code": response.status_code,
                "response": response.text
            }
    except requests.exceptions.RequestException as e:
        print("An error occurred while creating the test case version: {}".format(str(e)))
        return {"error": str(e)}

    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python2 Custom-Status-Priority-Fields.py <project_id>")
        sys.exit(1)

    print("Received arguments:", sys.argv)  # Debugging line

    project_id = sys.argv[1]

    # Fetch the JWT token
    context_jwt = get_jwt()
    if context_jwt:
        create_version(context_jwt, project_id)
    else:
        print("Failed to retrieve JWT token. Exiting.")

    print("Finished processing project ID '{}'.".format(project_id))
