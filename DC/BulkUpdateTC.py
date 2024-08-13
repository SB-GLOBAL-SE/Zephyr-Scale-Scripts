import requests
from requests.auth import HTTPBasicAuth

#Replace with your basic auth credentials
username = 'matthew.bonner'
password = 'pzg3abn_ndx9CKN4wrg'

#Replace with your host
host = 'https://next-jira-8-postgres.qa.tm4j-server.smartbear.io'

# Replace with testCaseKeys you wish to update IE [MIGB-T6235', 'MIGB-T6234', 'MIGB-T6233', 'MIGB-T6232', 'MIGB-T6231]
test_case_keys = ['MIGB-T6235', 'MIGB-T6234', 'MIGB-T6233', 'MIGB-T6232', 'MIGB-T6231']


url_template = '{host}/rest/atm/1.0/testcase/{testCaseKey}'

"""
In this example we update the labels for the given test cases. If you wish to modify other objects, follow API documentation specified here: https://support.smartbear.com/zephyr-scale-server/api-docs/v1/
You must also account for those objects in the payload (line 48) like labels.

The endpoint is: /rest/atm/1.0/testcase/{testCaseKey} 
Examples of objects we can update: 
{
  "projectKey": "JQA",
  "name": "Ensure the axial-flow pump is enabled",
  "precondition": "The precondition.",
  "objective": "The objective.",
  "folder": "/Orbiter/Cargo Bay",
  "status": "Approved",
  "priority": "Low",
  "component": "Valves",
  "owner": "vitor.pelizza",
  "estimatedTime": 138000,
  "labels": ["Smoke", "Functional"],
  "issueLinks": ["JQA-123", "JQA-456"],
  "customFields": {
    "single choice": "Propulsion engines",
    "multichoice": "Brazil, England"
  },
  "testScript": {
    "type": "STEP_BY_STEP",
    "steps": [
      {
        "description": "Ignite the secondary propulsion engines.",
        "testData": "Combustion chamber's initial pressure: 10",
        "expectedResult": "Ensure the high-pressure combustion chamber's pressure is around 3000 psi."
      }
    ]
  }
}
"""


# Values we are updating to the test case
payload = {
    "labels": ["BulkUpdate1", "BulkUpdate2"]
    # Add other fields as needed
}



# Headers
headers = {
    'Content-Type': 'application/json'
}

# Iterate through the list and send PUT requests
for test_case_key in test_case_keys:
    url = url_template.format(testCaseKey=test_case_key)
    response = requests.put(url, json=payload, headers=headers, auth=HTTPBasicAuth(username, password))
    
    # Print response status for each request
    print(f'Succcess, {test_case_key}')

    # Optional: Check the response content
    if response.status_code != 200:
        print(f'Error with {test_case_key}: {response.content}')
