import requests
import sys
from requests.auth import HTTPBasicAuth
import json
import os

# Clear error.txt if it exists from a previous run
if os.path.exists("error.txt"):
    os.remove("error.log")

if len(sys.argv) != 5:
    print("Usage: python3 MigrateExecutionStatus.py <username> <password> <project_key> <instance url> ")
    sys.exit(1)
with open('app.properties', 'r') as file:
    for line in file:
        if line.startswith('host'):
            # Split the line on '=' and strip any whitespace
            instance_url = line.split('=', 1)[1].strip()
            break


username = sys.argv[1]
password = sys.argv[2]
project_key = sys.argv[3]
instance_url = sys.argv[4]
base_url = instance_url
mc_auth = HTTPBasicAuth(username, password)

query_url = f"{base_url}/rest/api/2/search?jql=project = {project_key} AND issuetype = Test & maxResults=1"
default_headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# First API call to get issues data
issues_response = requests.get(query_url, headers=default_headers, auth=mc_auth)

# Check if the request was successful (status code 200)
if issues_response.status_code == 200:
    response_data = issues_response.json()

    # Check if there are issues in the response
    if "issues" in response_data and response_data["issues"]:
        first_issue = response_data["issues"][0]

        issue_id = first_issue["id"]
        project_id = first_issue["fields"]["project"]["id"]

        print(f"IssueID: {issue_id}")
        print(f"ProjectID: {project_id}")

        # Second API call to get execution details based on the retrieved issue ID
        query_url_execution = f"{base_url}/rest/zapi/latest/execution/?issueId={issue_id}"
        execution_response = requests.get(query_url_execution, headers=default_headers, auth=mc_auth)
        execution_data = execution_response.json()

        # Check if the request for execution details was successful (status code 200)
        if execution_response.status_code == 200:
            status_json = execution_data["status"]
            print("Execution details retrieved successfully.")
        else:
            # Save the error details to an "error.txt" file
            with open("error.txt", "w") as error_file:
                error_file.write(f"Error: {execution_response.status_code} - {execution_response.text}")
            print(f"Error: {execution_response.status_code} - {execution_response.text}\nError details saved to error.txt")
            sys.exit(1)
    else:
        print("No issues found in the response.")
        sys.exit(1)
else:
    with open("error.txt", "w") as error_file:
        error_file.write(f"Error: {issues_response.status_code} - {issues_response.text}")
    print(f"Error: {issues_response.status_code} - {issues_response.text}\nError details saved to error.txt")
    sys.exit(1)

# Your API endpoint for posting status
PostStatusURL = f"{base_url}/rest/tests/1.0/testresultstatus"

# Iterate through status.json and send requests
for status_id, status_details in status_json.items():
    payload = {
        "projectId": int(project_id),
        "name": status_details["name"],
        "description": status_details["description"],
        "color": status_details["color"],
        "index": int(status_id),
        "items": []
    }

    # Send the request
    response = requests.post(PostStatusURL, json=payload, headers=default_headers, auth=mc_auth)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print(f"Status {status_id} posted successfully.")
    else:
        # Write the error to error.txt
        with open("error.txt", "a") as error_file:
            error_file.write(f"Error posting status {status_id}: {response.status_code} - {response.text}\n")
        print(f"Error posting status {status_id}. Error details saved to error.txt")