import requests
from requests.auth import HTTPBasicAuth
import json

# Replace with the Jira credentials
username = '<Jira_username>' 
password = '<Jira_password>'
# Replace with the test cycle which contains the executions you wish to update
test_cycle = '<test_cycle>' 
# Replace with the Jira Base URL
base_url = '<jira_base_url>/rest/atm/1.0'


"""
In this example we update the plannedStartDate and plannedEndDate for all test executions within a cycle. If you wish to modify other objects, follow API documentation specified here: https://support.smartbear.com/zephyr-scale-server/api-docs/v1/
You must also account for those objects in the payload (line 72) like in lines 73 + 74 for the plannedStartDate and plannedEndDate.

The endpoint is: /testrun/{testRunKey}/testcase/{testCaseKey}/testresult 
Examples of objects we can update: 
{
  "status": "Fail",
  "environment": "Firefox",
  "comment": "The test has failed on some automation tool procedure.",
  "assignedTo": "vitor.pelizza",
  "executedBy": "cristiano.caetano",
  "executionTime": 180000,
  "actualStartDate": "2016-02-14T19:22:00-0300",
  "actualEndDate": "2016-02-15T19:22:00-0300",
  "customFields": {
    "CI Server": "Bamboo"
  },
  "issueLinks": ["JQA-123", "JQA-456"],
  "scriptResults": [
    {
      "index": 0,
      "status": "Fail",
      "comment": "This step has failed."
    }
  ]
}"""

#Data we are updating for all executions in a cycle
plannedStartDate = "2001-02-14T19:22:00-0300"
plannedEndDate = "2001-02-15T19:22:00-0300"



url = f'{base_url}/testrun/{test_cycle}'

headers = {
    'Content-Type': 'application/json'
}

response = requests.get(url, headers=headers, auth=HTTPBasicAuth(username, password))
CycleExecutions = []

if response.status_code == 200:
    CycleExecutions = response.content
    cycle_executions_dict = json.loads(CycleExecutions)
    items = cycle_executions_dict.get("items")
else:
    print('Error')
    print(response.status_code)

if items:
    for item in items:

        testCaseKey = item.get('testCaseKey')
        testExecutionStatus = item.get('status')
        url = f'{base_url}/testrun/{test_cycle}/testcase/{testCaseKey}/testresult'
        #Payload we are sending to update the test executions in the cycle
        payload = {
            "plannedStartDate": plannedStartDate,
            "plannedEndDate": plannedEndDate ,
            "status" : testExecutionStatus
        }
                 
        response = requests.put(url, headers=headers, json=payload, auth=HTTPBasicAuth(username, password))
        if response.status_code == 200:
            print("Succesfully Update Actual Start Date and Actual End Date")
        else:
            print("Failure")
            print(response.content)
else:
    print("No items found in the response.")