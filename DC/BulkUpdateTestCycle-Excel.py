import csv
import requests
from requests.auth import HTTPBasicAuth

# Replace with your basic auth credentials
username = '<username>'

password = '<password>'

# Replace with your host
host = '<host>'

# The CSV file path (since it's in the same directory as the script)
csv_file_path = 'inputfile.csv'

# API endpoint template
url_template = f'{host}/rest/atm/1.0/testcase/{{testCaseKey}}'

# Headers
headers = {
    'Content-Type': 'application/json'
}

# Read the CSV file
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
            user_pick = row ['userpicker (teststep custom field)']
            
            # Define the payload for the API request using CSV data
            payload = {
                "priority": priority,
                "component": component,
                "customFields": {
                    "date": date,
                    "number" : int(number),
                    "Single Line": single_line,
                    "Multi Line": multi_line,
                    "Single List": single_list,
                    "User pick" : user_pick
                }
            }

            # Create the URL for the specific test case
            url = url_template.format(testCaseKey=test_case_key)

            # Send the PUT request
            response = requests.put(url, json=payload, headers=headers, auth=HTTPBasicAuth(username, password))

            # Print response status for each request
            if response.status_code == 200:
                print(f'Successfully updated {test_case_key}')
            else:
                print(f'Error updating {test_case_key}: {response.status_code} - {response.content}')
                print(payload)
except FileNotFoundError:
    print(f"CSV file '{csv_file_path}' not found.")

