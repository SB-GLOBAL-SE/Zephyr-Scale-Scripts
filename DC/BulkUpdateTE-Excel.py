import requests
from requests.auth import HTTPBasicAuth
import json
import csv

# Replace with the Jira credentials
username = '<username>'
password = '<password>'
host = '<host>'
# Replace with your host
test_cycle = '<test_cycle>'
# Replace with the test cycle which contains the executions you wish to update

base_url = f'{host}/rest/atm/1.0'

url = f'{base_url}/testrun/{test_cycle}'

headers = {
    'Content-Type': 'application/json'
}
csv_file_path = 'inputfile1.csv'

response = requests.get(url, headers=headers, auth=HTTPBasicAuth(username, password))
CycleExecutions = []

if response.status_code == 200:
    CycleExecutions = response.content
    cycle_executions_dict = json.loads(CycleExecutions)
    items = cycle_executions_dict.get("items", [])
else:
    print('Error retrieving cycle executions')
    print(response.status_code)

if items:
    try:
        with open(csv_file_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            
            # Create a dictionary to store CSV data
            csv_data = {}
            for row in csv_reader:
                test_case_key = row['Test_case_keys']
                csv_data[test_case_key] = row

        for item in items:
            testCaseKey = item.get('testCaseKey')
            testExecutionStatus = item.get('status')
            
            # Check if the testCaseKey exists in the CSV data
            if testCaseKey in csv_data:
                row = csv_data[testCaseKey]
                
                url = f'{base_url}/testrun/{test_cycle}/testcase/{testCaseKey}/testresult'

                plannedStartDate = "2001-02-14T19:22:00-0300"
                plannedEndDate = "2001-02-15T19:22:00-0300"

                payload = {
                    "plannedStartDate": plannedStartDate,
                    "plannedEndDate": plannedEndDate,
                    "status": testExecutionStatus,
                    "customFields": {
                        "date": row['Date(testcase custom field)'],
                        "number": int(row['Number (testcase custom field)']),
                        "Single Line": row['Sinlge Line (testcase custom field)'],
                        "Multi Line": row['Multi Line (testcase custom field)'],
                        "Single List": row['Single List (testcase custom field)'],
                    }
                }

                response = requests.put(url, headers=headers, json=payload, auth=HTTPBasicAuth(username, password))
                if response.status_code == 200:
                    print(f"Successfully updated test case {testCaseKey}")
                else:
                    print(f"Failed to update test case {testCaseKey}")
                    print(response.content)
            else:
                print(f"Test case {testCaseKey} not found in CSV data")

    except FileNotFoundError:
        print(f'CSV file not found: {csv_file_path}')
else:
    print('No items found in the test cycle')
