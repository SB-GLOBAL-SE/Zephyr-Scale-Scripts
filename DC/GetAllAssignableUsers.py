import sys
import json
import requests
from requests.auth import HTTPBasicAuth

if len(sys.argv) != 5:
    print("Usage: python3 script.py <username> <password> <instance_url> <projectKey>")
    sys.exit(1)

#Note make sure projectKey is capatlized. 

username = sys.argv[1]
password = sys.argv[2]
base_url = sys.argv[3]
projectKey = sys.argv[4]

mc_auth = HTTPBasicAuth(username, password)
url = f"{base_url}/rest/api/2/user/assignable/search"
default_headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}
AssignableParams = {
    'username': '', 
    'project' : projectKey, 
    'startAt': 0,
    'maxResults': 1000,
    'active': True
}

response = requests.get(
    url=url,
    params=AssignableParams,
    auth=mc_auth,
    headers=default_headers
)


file_path = "AssignableUsers.txt"

if response.status_code == 200:
    users = response.json()
    with open(file_path, 'w') as file:
        for user in users:
            
            file.write(f"Username: {user['name']}, Display Name: {user['key']}\n")
            
else:
    print(f"Failed to retrieve users: {response.status_code}")
    print(response.content)
