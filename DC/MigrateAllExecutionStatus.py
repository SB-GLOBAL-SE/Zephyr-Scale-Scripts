import requests
import sys
from requests.auth import HTTPBasicAuth
import json


with open("error.txt", "w"):
    pass

if len(sys.argv) != 5:
    print("Usage: python3 MigrateExecutionStatus.py <username> <password> <project_key>  <instance_url>")
    sys.exit(1)

username = sys.argv[1]
password = sys.argv[2]
project_key = sys.argv[3]
base_url = sys.argv[4]
mc_auth = HTTPBasicAuth(username, password)

project_key = project_key
base_url = base_url
query_url = f"{base_url}/rest/api/2/search?jql=project = {project_key} AND issuetype = Test & maxResults=1" 
default_headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

issues_response = requests.get(query_url, headers=default_headers, auth=mc_auth)

# Check if the request was successful (status code 200)
if issues_response.status_code == 200:
    with open("Squad_TC_Data.txt", "w") as file:
        file.write(issues_response.text)

    response_data = json.loads(issues_response.text)

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
        execution_data = json.loads(execution_response.text)
        # Check if the request for execution details was successful (status code 200)
        if execution_response.status_code == 200:
        
        
            # Save the response to a text file
            with open("Squad_Execution_Data.txt", "w") as file:
                file.write(execution_response.text)
            status_json = execution_data["status"]
            with open("status.json", "w") as status_file:
                json.dump(status_json, status_file, indent=2)
            print("Execution details saved to Squad_Execution_Data.txt")
        else:
            # Save the error details to an "error.txt" file
            with open("error.txt", "w") as error_file:
                error_file.write(f"Error: {execution_response.status_code} - {execution_response.text}")
            print(f"Error: {execution_response.status_code} - {execution_response.text}\nError details saved to error.txt")
    else:
        print("No issues found in the response.")
else:
    with open("error.txt", "w") as error_file:
        error_file.write(f"Error: {issues_response.status_code} - {issues_response.text}")
    print(f"Error: {issues_response.status_code} - {issues_response.text}\nError details saved to error.txt")

status_file_path = "status.json"
with open(status_file_path, "r") as status_file:
    status_data = json.load(status_file)

# Your API endpoint for posting status
PostStatusURL = f"{base_url}/rest/tests/1.0/testresultstatus"

# Iterate through status.json and send requests
for status_id, status_details in status_data.items():
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
            error_file.write(f"Error posting status {status_id}: {response.status_code} - {response}\n")
        print(f"Error posting status {status_id}. Error details saved to error.txt")