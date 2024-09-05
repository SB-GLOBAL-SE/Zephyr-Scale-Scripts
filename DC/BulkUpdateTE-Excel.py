import requests
from requests.auth import HTTPBasicAuth
import json
import csv

# Replace with the Jira credentials
username = '<username>'
password = '<password>'
host = '<host>'
# Replace with your host
test_cycle = '<test cycle>'
# Replace with the test cycle which contains the executions you wish to update

base_url = f'{host}/rest/atm/1.0'

url = f'{base_url}/testrun/{test_cycle}'

headers = {
    'Content-Type': 'application/json'
}
csv_file_path = 'inputfile.csv'

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

            # Iterate through each row in the CSV
            for row in csv_reader:
                test_case_key = row['Test_case_keys']  # Extract test case key from the CSV
                component = row['component']
                priority = row['priority']
                date = row['Date(testcase custom field)']
                number = row['Number (testcase custom field)']
                single_line = row['Sinlge Line (testcase custom field)']
                multi_line = row['Multi Line (testcase custom field)']
                single_list = row['Single List (testcase custom field)']

            for item in items:
                testCaseKey = item.get('testCaseKey')
                testExecutionStatus = item.get('status')
                # Create the URL for the specific test case
                url = f'{base_url}/testrun/{test_cycle}/testcase/{testCaseKey}/testresult'

                #data not in CSV but I wanted to update
                plannedStartDate = "2001-02-14T19:22:00-0300"
                plannedEndDate = "2001-02-15T19:22:00-0300"

                # Define the payload for the API request using CSV data
                payload = {
                    "plannedStartDate": plannedStartDate,
                    "plannedEndDate": plannedEndDate,
                    "status": testExecutionStatus,
                    "customFields": {
                        "date": date,
                        "number": int(number),
                        "Single Line": single_line,
                        "Multi Line": multi_line,
                        "Single List": single_list,
                    }
                }
                

                # Make the API request
                response = requests.put(url, headers=headers, json=payload, auth=HTTPBasicAuth(username, password))
                if response.status_code == 200:
                    print(f"Successfully updated test case {testCaseKey}")
                else:
                    print(f"Failed to update test case {testCaseKey}")
                    print(response.content)

    except FileNotFoundError:
        print(f'CSV file not found: {csv_file_path}')
else:
    print('No items found in the test cycle')
