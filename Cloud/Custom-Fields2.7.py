import requests
from requests.auth import HTTPBasicAuth
import sys
import re
import json
import os

# In order to run the script, configure the fields below. Then run the python command with version 2.7 as the interpreter.
# EX: python2.7 Custom-Fields2.7-repo.py  <projectID>      
# EX: python2.7 Custom-Fields2.7-repo.py  10169

# To migrate custom feilds, we need to supply the project id as input.  

#### REPLACE ME WITH JIRA USER EMAIL #######   Requried for JWT and Custom Field functions
username = "<Jira User Email>"

#### REPLACE ME WITH JIRA API TOKEN #######    Requried for JWT and Custom Field functions
jira_api_token = "<Jira API Token>"

#### REPLACE <your-jira-instance> with the Jira instance #######       Requried for JWT and Custom Field functions
jwt_url = "https://<your-jira-instance>.atlassian.net/plugins/servlet/ac/com.kanoah.test-manager/main-project-page"


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
    if len(sys.argv) < 2:
        print("Usage: python2 Custom-Status-Priority-Fields.py <project_id>")
        sys.exit(1)

    print("Received arguments:", sys.argv)  # Debugging line

    # Treat the second argument as the project ID
    project_id = sys.argv[1]

    # Fetch the JWT token
    context_jwt = get_jwt()
    if context_jwt:
        create_custom_field(context_jwt, project_id)
    else:
        print("Failed to retrieve JWT token. Exiting.")

    print("Finished processing project ID '{}'.".format(project_id))